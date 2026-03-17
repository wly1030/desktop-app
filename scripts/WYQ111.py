# gravity deposition in box, showing how to plot and save history of data,
# and how to control the simulation while it is running by calling
# python functions from within the simulation loop
'''
finish:
step =  601 targeted porosity is met, save clump
the packings aabbDim()= (0.3000535211268496, 0.20006088222408527, 0.04981567910346166)
'''
################### line 23-24need to be upated every time############################
# import yade modules that we will use below

from builtins import range
from yade.gridpfacet import *
from yade import pack,ymport,export,geom,bodiesHandling, plot,utils,qt
import pylab
import matplotlib; matplotlib.rc('axes',grid=True)


##############parameters##########################################################################
import sys, json

intRadius = 1.5
leftTensilePos = -0.07
rightTensilePos = 2.29
normalStress = 100000
vel = -0.001/60.

box_n=2
A = 1.0 * 1.0*box_n*box_n
damping=0.4
alph=1e6

# 尝试从命令行参数读取前端传递的 JSON 数据并覆盖默认参数
if len(sys.argv) > 1:
    try:
        params = json.loads(sys.argv[1])
        if "in_radius" in params: intRadius = float(params["in_radius"])
        if "left_tension_pos" in params: leftTensilePos = float(params["left_tension_pos"])
        if "right_tension_pos" in params: rightTensilePos = float(params["right_tension_pos"])
        if "normal_stiffness" in params: normalStress = float(params["normal_stiffness"])
        if "vel" in params: vel = float(params["vel"])
        if "box_n" in params: box_n = float(params["box_n"])
        if "damping" in params: damping = float(params["damping"])
        if "alpha" in params: alph = float(params["alpha"])
        print("====== 成功加载应用配置参数 ======")
    except Exception as e:
        print("解析参数失败，将使用默认值:", e)

##############engine loop: recognize the interaction mechanism##########################################################################
O.engines = [
        ForceResetter(),
        InsertionSortCollider([
        	Bo1_Sphere_Aabb(aabbEnlargeFactor=intRadius,label='is2aabb'), 
        	Bo1_GridConnection_Aabb(),
        	Bo1_Facet_Aabb(),
        	Bo1_Wall_Aabb()
        ]),
        InteractionLoop(
                # handle sphere+sphere and facet+sphere collisions
                [
                	Ig2_Sphere_Sphere_ScGeom(interactionDetectionFactor=intRadius,label='ss2sc'), 
                	Ig2_Facet_Sphere_ScGeom(), 
                	Ig2_Wall_Sphere_ScGeom(),
                	Ig2_GridNode_GridNode_GridNodeGeom6D(),
                	Ig2_Sphere_GridConnection_ScGridCoGeom(),
                	Ig2_GridConnection_GridConnection_GridCoGridCoGeom()
                ],
                
                [
                	Ip2_FrictMat_FrictMat_FrictPhys(),
                	Ip2_CohFrictMat_CohFrictMat_CohFrictPhys(setCohesionNow=True, setCohesionOnNewContacts=False)
                ],
                
                [
                	Law2_ScGeom_FrictPhys_CundallStrack(),  # contact law for sphere-sphere
                	Law2_ScGridCoGeom_FrictPhys_CundallStrack(),  # contact law for cylinder-sphere
               	Law2_ScGeom6D_CohFrictPhys_CohesionMoment(),  # contact law for "internal" cylinder forces
               	Law2_GridCoGridCoGeom_FrictPhys_CundallStrack()  # contact law for cylinder-cylinder interaction
                ]
        ),
        NewtonIntegrator(gravity=(0, 0, 0), damping=0.1, label='newton'),#-9.81/alph
        #NewtonIntegrator(damping=damping,label='damper'),
        # call the checkUnbalanced function (defined below) every 2 seconds
        #VTKRecorder(iterPeriod=100000, recorders=['spheres','facets','boxes','stress','colors','intr'], fileName='vtkrecorder/p1-'),
        PyRunner(command='history()',iterPeriod=1),
        PyRunner(command='checkUnbalanced()', iterPeriod=1, label='checker'),
        PyRunner(command='vtk()', iterPeriod=10, label='vtk'),
        # call the addPlotData function every 200 steps
        PyRunner(command='addPlotData()', iterPeriod=100)
]

O.dt = 0.
O.step(); # to create initial contacts
# now reset the interaction radius and go ahead
ss2sc.interactionDetectionFactor=1.
is2aabb.aabbEnlargeFactor=1.



##############create geometry: clump, box, geosynthetics##########################################################################

O.materials.append(FrictMat(young=1e9,poisson=.4,frictionAngle=radians(40),density=2650*alph,label='spherefricMat'))
O.materials.append(FrictMat(young=1e9,poisson=.4,frictionAngle=0,density=2600*alph,label='frictionless'))
gridmatid = O.materials.append(
        CohFrictMat(
                young=2.13e9,#1.74e9,
                alphaKr=2,
                alphaKtw=2,
                poisson=0.3,
                density=800*alph,
                frictionAngle=radians(23),
                normalCohesion=9e9,
                shearCohesion=9e9,
                momentRotationLaw=True,
                label='gridmat'
        )
)


################################geogrid generation
L = 2.38  #length [m]   aperture size = 30 mm, grid_gap=35 mm
l = 2.03  #width	[m]
nbL = 68  #number of grids for the length	[#]
nbl = 58  #number of grids for the width	[#]
nbLL = nbL+1
nbll = nbl+1
r = 0.0025 #L / 100.  #radius
color = [255. / 255., 102. / 255., 0. / 255.]
nodesIds = []

#Create all nodes first :
for i in range(0, nbLL):
	for j in range(0, nbll):
		nodesIds.append(O.bodies.append(gridNode([i * L / nbL-0.08, j * l / nbl, -0.0025], r, wire=False, fixed=False, material='gridmat', color=color)))
#print(nodesIds)


#Create connection between the nodes
ConnectionIds1 = []
a_list=[]
b_list=[]
a_list.extend(nodesIds[:-1])
a_list.extend(nodesIds[:-nbll])
b_list.extend(nodesIds[1:])
b_list.extend(nodesIds[nbll:])

geogrid_list=[]
#for i in range(0, len(nodesIds)):
	#for j in range(i + 1, len(nodesIds)):
#for i, j in zip(nodesIds[:-1], nodesIds[1:]):
for i, j in zip(a_list, b_list): #solution3, in a accurate list which conclude all ID number of the gridNode
		dist = (O.bodies[i].state.pos - O.bodies[j].state.pos).norm()
		if (dist <= L / nbL * 1.01):
			ConnectionIds1.append(O.bodies.append(gridConnection(i, j, r, color=color)))
			geogrid_list.append([i,j])
#print(geogrid_list)
leftNode = [O.bodies[s] for s in nodesIds if O.bodies[s].state.pos[0]<leftTensilePos] #left node
rightNode = [O.bodies[s] for s in nodesIds if O.bodies[s].state.pos[0]>rightTensilePos]#right node


##################### create rectangular box from facets
#O.bodies.append(geom.facetBox((.15, .5, .5), (.5, .5, .5), wallMask=31))
upper_boxid=O.bodies.append(geom.facetBox((.5*box_n, 0.5*box_n, 0.6124/2.+0.05), (.5*box_n, 0.5*box_n, 0.6124/2.+0.05), wallMask=15,material='frictionless'))
lower_boxid=O.bodies.append(geom.facetBox((.5*box_n, 0.5*box_n, -0.6124/2.-0.005), (.5*box_n, 0.5*box_n, 0.6124/2.), wallMask=31,material='frictionless'))
print('lower_boxid,upper_boxid',lower_boxid,upper_boxid)




##############################clump

# add clumps
print("Load clumps")
ymport.textClumps("savedClumps4.txt", shift=Vector3(0,0,0), material='spherefricMat')
ymport.textClumps("savedClumps4.txt", shift=Vector3(0,0,-0.6124-0.005), material='spherefricMat')

#add the top wall
zMax=aabbExtrema()[1][2]
wallid=O.bodies.append(wall((0,0,zMax),2,material='frictionless'))
O.bodies[wallid].state.mass = 1000000
O.bodies[wallid].state.blockedDOFs = 'XYZxyz'
'''
#add side facet
zMax=aabbExtrema()[1][2]
facets = []
v1 = Vector3( 2,0 , -0.005 )
v2 = Vector3(2.3,0 , -0.005)
v3 = Vector3(2.3,2 , -0.005)
v4 = Vector3( 2,2 , -0.005)
f1_right = facet((v1,v3,v2),color=(0,0,1),material='frictionless')
f2_right = facet((v1,v4,v3),color=(0,0,1),material='frictionless')

v5 = Vector3( 0,0 , -0.005 )
v6 = Vector3(-0.1,0 , -0.005)
v7 = Vector3(-0.1,2 , -0.005)
v8 = Vector3( 0,2 , -0.005)
f1_left = facet((v5,v7,v6),color=(0,0,1),material='frictionless')
f2_left = facet((v5,v8,v7),color=(0,0,1),material='frictionless')

facets.extend((f1_right,f2_right,f1_left,f2_left))
O.bodies.append(facets)
#mass = O.bodies[0].state.mass
for f in facets:
	f.state.mass = 1000000
	f.state.blockedDOFs = 'XYZxyz'
'''

'''
#definition for getting informations from all clumps:
def getClumpInfo():
	for b in O.bodies:
		if b.isClump:
			print('Clump ',b.id,' has following members:')
			keys = list(b.shape.members.keys())
			for ii in range(0,len(keys)):
				print('- Body ',keys[ii])
			print('inertia:',b.state.inertia)
			print('mass:',b.state.mass,'\n')


getClumpInfo()
'''
#### show how to use getRoundness():
#create a list of all standalone spheres:
standaloneList = []
for b in O.bodies:
	if b.isStandalone:
		standaloneList.append(b.id)
clumpList = []
for b in O.bodies:
	if b.isClump:
		clumpList.append(b.id)
clump_memberList = []
for b in O.bodies:
	if b.isClumpMember:
		clump_memberList.append(b.id)		
print(len(standaloneList),' non-clump particles generated.')
print(len(clumpList),' clumps generated.')
print('Roundness coefficient for spheres and clumps is: ',O.bodies.getRoundness())
print('Roundness coefficient just for clumps is: ',O.bodies.getRoundness(standaloneList))


print('the upper position of the clump sample', aabbExtrema()[1][2])
mm,mx=[pt[0] for pt in aabbExtrema()] #the left and the right pos
print (mm,mx)

# time step
O.dt = .5 * PWaveTimeStep()
print ("dt = ", O.dt)
##############pyrunner for: mechanical simulation &&& output data data mining ##########################################################################

# the following checkUnbalanced, unloadPlate and stopUnloading functions are all called by the 'checker'
# (the last engine) one after another; this sequence defines progression of different stages of the
# simulation, as each of the functions, when the condition is satisfied, updates 'checker' to call
# the next function when it is run from within the simulation next time


# check whether the gravity deposition has already finished
# if so, add wall on the top of the packing and start the oedometric test
def checkUnbalanced():
	# at the very start, unbalanced force can be low as there is only few contacts, but it does not mean the packing is stable
	if O.iter < 0:
		return
	# the rest will be run only if unbalanced is < .1 (stabilized packing)
	#if unbalancedForce() > .1:
	#	return
	# add plate at the position on the top of the packing
	# the maximum finds the z-coordinate of the top of the topmost particle
	#O.bodies.append(wall(max([b.state.pos[2] + b.shape.radius for b in O.bodies if isinstance(b.shape, Clump)]), axis=2, sense=-1))
	
	O.bodies[wallid].state.blockedDOFs = 'XYZxy'
	for s in leftNode:
			s.shape.color = (1,0,0)
			s.state.blockedDOFs = 'xyzXYZ'

			
	for s in rightNode:
			s.shape.color = Vector3(0,1,0)
			s.state.blockedDOFs = 'xyzXYZ'

	#apply force on the top wall
	if O.iter >= 0:
		O.forces.setPermF(wallid,(0,0,-1*normalStress*A))
		#O.forces.addF(wallid,(0,0,-1*normalStress*A))
	
	
	#move the lower shear box:
	if O.iter >= 50000:
		for low in lower_boxid:
			O.bodies[low].state.blockedDOFs = 'xyzXYZ'
			O.bodies[low].state.vel = (vel,0.,  0.)
			########????????whether need to set the rotation freedom?
		#for f in facets:
			#O.bodies[f].state.blockedDOFs = 'xyzXYZ'
			#f.state.vel = ( vel, 0, 0)
	
		for s in leftNode:
			s.shape.color = (1,0,0)
			#s.state.blockedDOFs = 'xyzXYZ'
			s.dynamic = False
			s.state.vel = (vel,0,0)
			
		for s in rightNode:
			s.shape.color = Vector3(0,1,0)
			#s.state.blockedDOFs = 'xyzXYZ'
			s.dynamic = False
			s.state.vel = (vel,0,0)	

	
	
	#print('facet force',O.forces.f(0)[1] )
	lowbox = O.bodies[lower_boxid[0]]
	dspl = -1*lowbox.state.displ()[0]
	#if O.iter % 100 == 0:
		#print( 'shear displacement = ', dspl)
		#print ('p = ', poros)
	if dspl >= 0.01:
		plot.saveDataTxt(O.tags['d.id'] + '.txt')
		#O.pause()
def history():
	'''
	if O.iter % 100 == 0:
		F_file=open("shearStress"+str(O.iter)+".txt","w")
		for intr in O.interactions:
			id1,id2=intr.id1,intr.id2
			body1,body2=[O.bodies[i] for i in (id1,id2)]
			m1,m2=[b.mat.label for b in (body1,body2)]
			#print (id1,id2,m1,m2,intr.phys)
			s1=str(id1)+'\t'+str(id2)+'\t'+str(m1)+'\t'+str(m2)+'\t'+str(intr.phys)+'\n'

			F_file.write(s1)	
	'''

def vtk():
	if O.iter % 100000 == 0:
		vtkExporter1 = export.VTKExporter('vtkrecorder/gg1-'+str(O.iter)) #/tmp/vtkExporterTesting
		vtkExporter1.exportInteractions(ids=geogrid_list,what=dict(normalForce='i.phys.normalForce.norm()')) #geogrid rib visualization, radius= r, #i.phys.normalForce.norm()

	if O.iter % 100000 == 0:		
		vtkExporter2 = export.VTKExporter('vtkrecorder/clump1-'+str(O.iter)) #/tmp/vtkExporterTesting
		vtkExporter2.exportSpheres(ids=clump_memberList, what=dict(disp='b.state.displ().norm',pos='b.state.pos',orient='b.state.rot()',velocity='b.state.vel')) #[i for i in clumpList]
	
	
	if O.iter % 100000 == 0:
		clump_intrID=[]
		for intr in O.interactions:
			id1,id2=intr.id1,intr.id2
			body1,body2=[O.bodies[i] for i in (id1,id2)]
			m1,m2=[b.mat.label for b in (body1,body2)]
			if (m1 == 'spherefricMat') and (m2 == 'spherefricMat'):
				clump_intrID.append([id1,id2])
		vtkExporter3 = export.VTKExporter('vtkrecorder/f-network1-'+str(O.iter)) #/tmp/vtkExporterTesting
		vtkExporter3.exportInteractions(ids=clump_intrID, what=dict(normalForce='i.phys.normalForce',normalForce1='i.phys.normalForce.norm()')) #[i for i in clumpList]

	
	#vtkExporter.exportFacets(what={'pos':'b.state.pos'})
	#vtkExporter.exportContactPoints(what={'nn':'i.geom.normal'})
	#vtkExporter.exportPolyhedra(what=dict(n='b.id'))

def addPlotData():
	if not isinstance(O.bodies[-1].shape, Wall):
		plot.addData()
		return
	
	F_top = O.forces.f(wallid)[2]
	top_y = O.bodies[wallid].state.pos[2]
	
	#fs=sum(O.forces.f(ii)[1] for ii in lower_boxid)
	fs=0.0
	for i in upper_boxid:
		fs += O.forces.f(i)[0]
	shearStress=-1*fs/A/1000.
		
	lowbox = O.bodies[lower_boxid[0]]
	dspl = -1*lowbox.state.displ()[0]
	bottom_z= lowbox.state.pos[2]
	f_bottom = 0
	
	#geogrid output
	#f_leftNode = sum(O.forces.f(b.id)[0] for b in leftNode)
	#f_rightNode = sum(O.forces.f(b.id)[0] for b in rightNode)
	
	#f_leftConnection = sum(O.forces.f(b.id)[0] for b in leftConnection)
	#f_rightConnection = sum(O.forces.f(b.id)[0] for b in rightConnection)
	
	#f_both = .5*(-f_rightNode+f_leftNode)
	#f =f_leftNode
	#s = f/(pi*.25*width*width) if testType=='cyl' else f/(width*width) if testType=='cube' else None
	#strain = (rightNode[0].state.displ()[0] - leftNode[0].state.displ()[0]) / (mx-mm)*100 #[%]
	
	
	
	for i in lower_boxid:
		f_bottom += O.forces.f(i)[2]
		
	
	print('step = ', O.iter,'F_top=',F_top,'f_bottom=',f_bottom,'bottom_z',bottom_z,'top_y=',top_y,'fs',fs,'dspl=',dspl)
	
	plot.addData(dspl=dspl,F_top=F_top, top_y=top_y,shearStress=shearStress,w=O.bodies[wallid].state.pos[2] - O.bodies[wallid].state.refPos[2], unbalanced=unbalancedForce(), i=O.iter,porosity=porosity(),coordination=avgNumInteractions())#the porosity's total volume V can be self-defined, P718, volume=volume


# besides unbalanced force evolution, also plot the displacement-force diagram
plot.plots = {'i': ('unbalanced',None,'top_y'), 'dspl': ('shearStress',)} #'i': ('unbalanced',None,'fs'), 
plot.plot()

'''
# enable energy tracking; any simulation parts supporting it
# can create and update arbitrary energy types, which can be
# accessed as O.energy['energyName'] subsequently
O.trackEnergy = True


# if the unbalanced forces goes below .05, the packing
# is considered stabilized, therefore we stop collected
# data history and stop
def checkUnbalanced():
	#if unbalancedForce() < .05:
		#O.pause()
	plot.saveDataTxt('bbb.txt.bz2')
		# plot.saveGnuplot('bbb') is also possible
	if O.iter == 10:
		print('step = ', O.iter)
		export.textClumps("savedClumps3.txt")

# collect history of data which will be plotted
def addPlotData():
	# each item is given a names, by which it can be the unsed in plot.plots
	# the **O.energy converts dictionary-like O.energy to plot.addData arguments
	plot.addData(i=O.iter, unbalanced=unbalancedForce(),total=O.energy.total(),  **O.energy) #



# define how to plot data: 'i' (step number) on the x-axis, unbalanced force
# on the left y-axis, all energies on the right y-axis
# (O.energy.keys is function which will be called to get all defined energies)
# None separates left and right y-axis
plot.plots = {'i': ('unbalanced', None, O.energy.keys,)} #

# show the plot on the screen, and update while the simulation runs
plot.plot()

'''
##############start simulation##########################################################################
#O.saveTmp()
O.run()
qt.View()
#qt.views()
#rr = yade.qt.Renderer() #P545
#rr.bgColor=[225. / 255., 225. / 255., 225. / 255.]
#rr.shape = False
#rr.intrPhys = True
#rr.intrAllWire = True
#rr.light1 = True
#qt.View()
#vv = yade.qt.views()
