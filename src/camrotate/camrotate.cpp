
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

  // get rotation amounts about x,y,z axes (degrees)
  double vertical = ui.GetDouble("VERTICAL"); // x-axis pitch
  double horizontal = ui.GetDouble("HORIZONTAL"); // y-axis yaw
  double twist = ui.GetDouble("TWIST"); // z-axis roll

  // convert angles to radians
  horizontal *= rpd_c();
  vertical   *= rpd_c();
  twist      *= rpd_c();

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
  ConstSpiceDouble q[4] = {q0,q1,q2,q3};
  // SpiceDouble q[4] = {q0,q1,q2,q3};

  // translate quaternion to a rotation matrix using SPICE q2m
  SpiceDouble M[3][3];
  q2m_c(q, M);



  // translate to rotation matrix C and rotate with rotation matrices R
  // nowork

  // // rotate the rotation matrix to get a new one using SPICE rotmat
  // rotmat_c(M, horizontal, 2, M); // 2 is the y axis
  // rotmat_c(M, vertical,   1, M); // 1 is the x axis
  // rotmat_c(M, twist,      3, M); // 3 is the z axis

  // rotate the matrix M by the three angles

  // x-axis rotation: vertical (pitch)
  ConstSpiceDouble axisX[] = {M[0][0],M[0][1],M[0][2]}; // get x-axis //. better way?
  // ConstSpiceDouble axisX[] = {-1,0,0};
  SpiceDouble Rx[3][3];
  axisar_c ( axisX, vertical, Rx ); // get rotation matrix Rx
  mxm_c ( M, Rx, M ); // rotate matrix M by Rx

  // y-axis rotation: horizontal (yaw)
  ConstSpiceDouble axisY[] = {M[1][0],M[1][1],M[1][2]};
  // ConstSpiceDouble axisY[] = {0,1,0};
  SpiceDouble Ry[3][3];
  axisar_c ( axisY, horizontal, Ry );
  mxm_c ( M, Ry, M );

  // z-axis rotation: twist (roll)
  ConstSpiceDouble axisZ[] = {M[2][0],M[2][1],M[2][2]};
  // ConstSpiceDouble axisZ[] = {0,0,1};
  SpiceDouble Rz[3][3];
  axisar_c ( axisZ, twist, Rz );
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




  // // rotate quaternion by other quaternions
  // // nowork - new quaternion was WAY different from original one

  // // get rotation quaternions
  // ConstSpiceDouble qPitch[] = {vertical,   M[0][0], M[1][0], M[2][0]};
  // ConstSpiceDouble qYaw[]   = {horizontal, M[0][1], M[1][1], M[2][1]};
  // ConstSpiceDouble qRoll[]  = {twist,      M[0][2], M[1][2], M[2][2]};

  // // rotate original quaternion
  // qxq_c ( q, qPitch, q );
  // qxq_c ( q, qYaw,   q );
  // qxq_c ( q, qRoll,  q );

  // // save the new quaternion to the table
  // record[0] = q[0];
  // record[1] = q[1];
  // record[2] = q[2];
  // record[3] = q[3];
  // table.Update(record, 0); // 0 is the record number




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
