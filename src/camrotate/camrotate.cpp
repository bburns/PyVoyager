
#include "Isis.h"

#include <iostream>

#include "Cube.h"
#include "Camera.h"
#include "CameraFactory.h"
#include "Table.h"

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

  // rotate the rotation matrix to get a new one using SPICE rotmat
  const double pi = 3.14159265358979323846;
  const double degToRad = pi / 180;

  double horizontalRads = horizontal * degToRad; // convert to radians
  double verticalRads   = vertical   * degToRad;
  double twistRads      = twist      * degToRad;

  rotmat_c(M, horizontalRads, 2, M); // 2 is the y axis
  rotmat_c(M, verticalRads,   1, M); // 1 is the x axis
  rotmat_c(M, twistRads,      3, M); // 3 is the z axis

  // translate rotation matrix to a quaternion using SPICE m2q
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

  //. add a history record

  // close cube file
  cube.close();

}
