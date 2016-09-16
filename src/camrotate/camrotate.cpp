
#include "Isis.h"

#include <iostream>

#include "Cube.h"
#include "Camera.h"
#include "CameraFactory.h"
#include "Table.h"
#include "History.h"

#include <SpiceUsr.h>


using namespace std;
using namespace Isis;


void IsisMain() {

  UserInterface &ui = Application::GetUserInterface();

  // get cube filename
  QString filename = ui.GetFileName("FROM");

  // get rotation amounts about x,y,z axes
  double horizontal = ui.GetDouble("HORIZONTAL"); // y-axis (NOT x-axis)
  double vertical = ui.GetDouble("VERTICAL"); // x-axis (NOT y-axis)
  double twist = ui.GetDouble("TWIST"); // z-axis

  // open cube file
  Cube cube;
  cube.open(filename, "rw");

  // get camera
  Camera *cam = CameraFactory::Create(cube);

  // get instrument pointing table (set of quaternions with times)
  Table table = cam->instrumentRotation()->Cache("InstrumentPointing");

  // print the table
  cout << Table::toString(table);

  // there should just be one record in the table
  assert(table.Records()==1);

  // get the record
  TableRecord record = table[0];

  // get the quaternion from the record
  // record[0] etc are TableFields
  double q0 = record[0];
  double q1 = record[1];
  double q2 = record[2];
  double q3 = record[3];

  // translate quaternion to a rotation matrix using SPICE q2m
  ConstSpiceDouble q[4] = {q0,q1,q2,q3};
  SpiceDouble M[3][3];
  q2m_c(q, M);

  // convert angles to radians
  // const double pi = 3.14159265358979323846;
  // const double degToRad = pi / 180;
  // double horizontalRads = horizontal * degToRad;
  // double verticalRads   = vertical   * degToRad;
  // double twistRads      = twist      * degToRad;
  horizontal *= rpd_c();
  vertical   *= rpd_c();
  twist      *= rpd_c();

  // // rotate the rotation matrix to get a new one using SPICE rotmat
  // rotmat_c(M, horizontal, 2, M); // 2 is the y axis
  // rotmat_c(M, vertical,   1, M); // 1 is the x axis
  // rotmat_c(M, twist,      3, M); // 3 is the z axis

  // get axes to rotate about
  //. must be a better way to do this
  ConstSpiceDouble axisX[] = {M[0][0],M[0][1],M[0][2]};
  ConstSpiceDouble axisY[] = {M[1][0],M[1][1],M[1][2]};
  ConstSpiceDouble axisZ[] = {M[2][0],M[2][1],M[2][2]};
  // ConstSpiceDouble axisX[] = {M[0][0],M[1][0],M[2][0]};
  // ConstSpiceDouble axisY[] = {M[0][1],M[1][1],M[2][1]};
  // ConstSpiceDouble axisZ[] = {M[0][2],M[1][2],M[2][2]};

  // get rotation matrices about the different axes using SPICE axisar
  SpiceDouble Rx[3][3];
  SpiceDouble Ry[3][3];
  SpiceDouble Rz[3][3];
  axisar_c ( axisX, vertical,   Rx );
  axisar_c ( axisY, horizontal, Ry );
  axisar_c ( axisZ, twist,      Rz );

  // rotate camera pointing matrix by rotation matrices
  mxm_c ( M, Rx, M );
  mxm_c ( M, Ry, M );
  mxm_c ( M, Rz, M );

  // translate rotation matrix back to a quaternion using SPICE m2q
  SpiceDouble qnew[4];
  m2q_c(M, qnew);

  // save the new quaternion to the table
  record[0] = qnew[0];
  record[1] = qnew[1];
  record[2] = qnew[2];
  record[3] = qnew[3];
  table.Update(record, 0); // 0 is the record number

  // print the new table
  cout << Table::toString(table);

  // save table to the cube file
  cube.write(table);

  // add a history record for this command and parameters
  History hist = History("IsisCube");
  try {
    cube.read(hist); // read history from cube, if it exists.
  }
  catch (IException &e) {
    // if the history does not exist in the cube, the cube's write method will add it.
  }
  hist.AddEntry();
  cube.write(hist);

  // close cube file
  cube.close();

}
