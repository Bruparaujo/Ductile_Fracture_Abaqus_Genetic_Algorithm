import random  
import numpy as np  
from deap import base, creator, tools, algorithms  
from abaqus import *  
from abaqusConstants import *  
from caeModules import *  
from driverUtils import executeOnCaeStartup  
import odbAccess  
    
executeOnCaeStartup()  
session.journalOptions.setValues(replayGeometry=INDEX, recoverGeometry=INDEX)  
    
#: Tensile Test  
data = np.genfromtxt('C:\\temp\\GTN-PADRAO.txt')  
NumPT = len(data)  
NECK = 4.1/2  
R0 = 6.09/2  
L0 = 23.6/2  
    
#Function Parameters Definition  
nglobal_max = 3  
nbits = []  
min_ = []     
max_ = []  
oper0 = [0]*NumPT  
oper1 = oper2 = 0  
    
#Parameter 1: q1  
nbits.append(3)  
min_.append(1.4)  
max_.append(1.6)  
#Parameter 2: q2  
nbits.append(3)  
min_.append(1)  
max_.append(1.1)  
#Parameter 3: f0  
nbits.append(10)  
min_.append(0.998977)  
max_.append(1.000000)  
#Parameter 4: ff  
nbits.append(6)  
min_.append(0.01)  
max_.append(0.64)  
#Parameter 5: fc  
nbits.append(8)  
min_.append(0.001)  
max_.append(0.256)  
#Parameter 6: fn  
nbits.append(7)  
min_.append(0.000)  
max_.append(0.127)  
#Parameter 7: En  
nbits.append(5)  
min_.append(0.07)  
max_.append(0.38)  
#Parameter 8: Sn  
nbits.append(7)  
min_.append(0.005)  
max_.append(0.132)  
    
#Genetic Algorithm Parameters Definition  
Pop_Size = 50      #Population Size  
print "Population = "+str(Pop_Size)  
NGen = 100         #Generation Number  
print "Generation = "+str(NGen)  
CXPB = 0.8         #Crossover Probability  
MutPB = 0.2        #Mutation Probability of each individual  
IndPB = 0.05       #Probability of each gene to mutate  
Tournament = 2     #Individuals to crossover  
    
    
#: ABAQUS  
#: Creating Model  
mdb.Model(name='GTN_CP', modelType=STANDARD_EXPLICIT)  
#: Part  
s = mdb.models['GTN_CP'].ConstrainedSketch(name='__profile__', sheetSize=200.0)  
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints  
s.sketchOptions.setValues(viewStyle=AXISYM)  
s.setPrimaryObject(option=STANDALONE)  
s.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))  
s.FixedConstraint(entity=g[2])  
s.rectangle(point1=(0.0, 0.0), point2=(R0, L0))  
s.CoincidentConstraint(entity1=v[0], entity2=g[2], addUndoState=False)  
p = mdb.models['GTN_CP'].Part(name='CP', dimensionality=AXISYMMETRIC, type=DEFORMABLE_BODY)  
p = mdb.models['GTN_CP'].parts['CP']  
p.BaseShell(sketch=s)  
s.unsetPrimaryObject()  
p = mdb.models['GTN_CP'].parts['CP']  
del mdb.models['GTN_CP'].sketches['__profile__']  
#: Creating Model END  
    
#: Creating Material  
mdb.models['GTN_CP'].Material(name='STEEL')  
mdb.models['GTN_CP'].materials['STEEL'].Density(table=((7.85e-09, ), ))  
mdb.models['GTN_CP'].materials['STEEL'].Elastic(table=((219690.0, 0.3), ))  
mdb.models['GTN_CP'].materials['STEEL'].Plastic(table=((507.334397,   
), (549.5097044, 0.000498704), (589.8508529, 0.001315076), (614.2308965,   
), (633.6845798, 0.003115551), (649.7991599, 0.0040422), (  
, 0.004981341), (674.8624385, 0.005928115), (689.430522,   
), (727.0541669, 0.011690545), (761.2557359, 0.016534864), (  
, 0.021402538), (814.9560912, 0.026290427), (835.9965864,   
), (854.0576758, 0.036112442), (869.3072179, 0.041043028), (  
, 0.045983239), (893.1472119, 0.050934511), (902.4773937,   
), (910.4291914, 0.060855846), (918.0804833, 0.065821018), (  
, 0.070793954), (929.9363873, 0.075767052), (936.3031444,   
), (941.9769986, 0.085712245), (947.3756487, 0.090687671), (  
, 0.095664227), (957.4508428, 0.10064181), (962.1703286,   
), (966.701725, 0.110599701), (971.0602353, 0.115579861), (  
, 0.120560748), (979.3106819, 0.125542307), (983.2250718,   
), (987.0118924, 0.135507252), (990.6796414, 0.140490557), (  
, 0.145474369), (997.6878443, 0.150458656), (1001.041527,   
), (1004.302762, 0.160428546), (1007.476786, 0.165414098), (  
, 0.170400026), (1013.582, 0.175386308), (1016.521649,   
), (1019.391087, 0.185359866), (1022.193773, 0.190347108), (  
, 0.19533464), (1069.814028, 0.295130347), (1102.844742,   
), (1129.166151, 0.494860184), (1151.138029, 0.594760171), (  
, 0.694674094), (1186.679978, 0.794598389), (1201.54635,   
), (1215.002538, 0.994469468), (1227.304932, 1.094413469)))  
#: Section Create  
mdb.models['GTN_CP'].HomogeneousSolidSection(name='Section-CP', material='STEEL', thickness=None)  
#: Set ALL  
p = mdb.models['GTN_CP'].parts['CP']  
f = p.faces  
faces = f.getSequenceFromMask(mask=('[#1 ]', ), )  
region = p.Set(faces=faces, name='ALL')  
#: Section Assign  
p = mdb.models['GTN_CP'].parts['CP']  
p.SectionAssignment(region=region, sectionName='Section-CP', offset=0.0,   
    offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)  
#: Creating Material END  
    
#: Creating Assembly  
a = mdb.models['GTN_CP'].rootAssembly  
a.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0),   
    point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))  
p = mdb.models['GTN_CP'].parts['CP']  
a.Instance(name='CP-1', part=p, dependent=OFF)  
#: Creating Assembly END  
    
#: Step-1  
mdb.models['GTN_CP'].ExplicitDynamicsStep(name='Step-1', previous='Initial',   
    timePeriod=1.0, massScaling=((SEMI_AUTOMATIC, MODEL, AT_BEGINNING,   
, 1.8e-05, BELOW_MIN, 1, 0, 0.0, 0.0, 0, None), ))  
    
mdb.models['GTN_CP'].fieldOutputRequests['F-Output-1'].setValues(variables=(  
    'S', ), numIntervals=1)  
    
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
edges1 = e1[2:3]  
a.Set(edges=edges1, name='TOP')  
regionDef=mdb.models['GTN_CP'].rootAssembly.sets['TOP']  
mdb.models['GTN_CP'].historyOutputRequests['H-Output-1'].setValues(variables=(  
    'RF2', ), numIntervals=100, region=regionDef, sectionPoints=DEFAULT,   
    rebar=EXCLUDE)  
    
a = mdb.models['GTN_CP'].rootAssembly  
v1 = a.instances['CP-1'].vertices  
verts1 = v1[2:3]  
a.Set(vertices=verts1, name='No-U')  
regionDef=mdb.models['GTN_CP'].rootAssembly.sets['No-U']  
mdb.models['GTN_CP'].HistoryOutputRequest(name='H-Output-2',   
    createStepName='Step-1', variables=('U2', ), numIntervals=100,   
    region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)  
    
#: Creating Boundary Condition  
#: BC-NECK  
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
edges1 = e1[0:1]  
region = a.Set(edges=edges1, name='NECK')  
mdb.models['GTN_CP'].DisplacementBC(name='BC-NECK', createStepName='Initial',   
    region=region, u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET,  
    distributionType=UNIFORM, fieldName='', localCsys=None)  
#: BC-AXIS  
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
edges1 = e1[3:4]  
region = a.Set(edges=edges1, name='AXIS')  
mdb.models['GTN_CP'].DisplacementBC(name='BC-AXIS', createStepName='Initial',   
    region=region, u1=SET, u2=UNSET, ur3=UNSET, amplitude=UNSET,   
    distributionType=UNIFORM, fieldName='', localCsys=None)  
    
#: Axial Load  
#: Amplitude  
mdb.models['GTN_CP'].TabularAmplitude(name='Amp-TOPSIDE', timeSpan=STEP,   
    smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.1, 3.0), (1.0, 3.0)))  
#: Velocity  
a = mdb.models['GTN_CP'].rootAssembly  
region = a.sets['TOP']  
mdb.models['GTN_CP'].VelocityBC(name='BC-VEL', createStepName='Step-1',   
    region=region, v1=UNSET, v2=1.0, vr3=UNSET, amplitude='Amp-TOPSIDE',   
    localCsys=None, distributionType=UNIFORM, fieldName='')  
#: Creating Boundary Condition END  
    
#: Creating Mesh  
elemType1 = mesh.ElemType(elemCode=CAX4R, elemLibrary=EXPLICIT,   
    secondOrderAccuracy=ON, hourglassControl=DEFAULT,   
    distortionControl=DEFAULT)  
elemType2 = mesh.ElemType(elemCode=CAX3, elemLibrary=EXPLICIT)  
a = mdb.models['GTN_CP'].rootAssembly  
f1 = a.instances['CP-1'].faces  
faces1 = f1.getSequenceFromMask(mask=('[#1 ]', ), )  
pickedRegions =(faces1, )  
a.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))  
#: Partition Face  
a = mdb.models['GTN_CP'].rootAssembly  
f1 = a.instances['CP-1'].faces  
t = a.MakeSketchTransform(sketchPlane=f1[0], sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))  
s1 = mdb.models['GTN_CP'].ConstrainedSketch(name='__profile__', sheetSize=41.23, gridSpacing=1.03, transform=t)  
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints  
s1.setPrimaryObject(option=SUPERIMPOSE)  
a = mdb.models['GTN_CP'].rootAssembly  
a.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)  
#: Partition Lines  
s1.Line(point1=(0.0, 0.3), point2=(3.045, 0.3))  
s1.HorizontalConstraint(entity=g[7], addUndoState=False)  
s1.PerpendicularConstraint(entity1=g[5], entity2=g[7], addUndoState=False)  
s1.CoincidentConstraint(entity1=v[4], entity2=g[5], addUndoState=False)  
s1.CoincidentConstraint(entity1=v[5], entity2=g[3], addUndoState=False)  
s1.Line(point1=(0.0, 0.5), point2=(3.045, 0.5))  
s1.HorizontalConstraint(entity=g[8], addUndoState=False)  
s1.PerpendicularConstraint(entity1=g[5], entity2=g[8], addUndoState=False)  
s1.CoincidentConstraint(entity1=v[6], entity2=g[5], addUndoState=False)  
s1.CoincidentConstraint(entity1=v[7], entity2=g[3], addUndoState=False)  
a = mdb.models['GTN_CP'].rootAssembly  
f1 = a.instances['CP-1'].faces  
pickedFaces = f1.getSequenceFromMask(mask=('[#1 ]', ), )  
a.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)  
s1.unsetPrimaryObject()  
del mdb.models['GTN_CP'].sketches['__profile__']  
#: Mesh Generate  
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
pickedEdges = e1.getSequenceFromMask(mask=('[#f5 ]', ), )  
a.seedEdgeBySize(edges=pickedEdges, size=0.1, deviationFactor=0.1,   
    constraint=FINER)  
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
pickedEndEdges = e1.getSequenceFromMask(mask=('[#a ]', ), )  
a.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges,  
    minSize=0.5, maxSize=1.5, constraint=FINER)  
a = mdb.models['GTN_CP'].rootAssembly  
e1 = a.instances['CP-1'].edges  
pickedEdges = e1.getSequenceFromMask(mask=('[#300 ]', ), )  
a.seedEdgeBySize(edges=pickedEdges, size=0.25, deviationFactor=0.1,   
    constraint=FINER)  
a = mdb.models['GTN_CP'].rootAssembly  
partInstances =(a.instances['CP-1'], )  
a.generateMesh(regions=partInstances)  
#: Creating Mesh END  
    
a = mdb.models['GTN_CP'].rootAssembly  
n1 = a.instances['CP-1'].nodes  
nodes1 = n1[148:149]  
a.Set(nodes=nodes1, name='No-Neck')  
regionDef=mdb.models['GTN_CP'].rootAssembly.sets['No-Neck']  
mdb.models['GTN_CP'].HistoryOutputRequest(name='H-Output-3',   
    createStepName='Step-1', variables=('COOR1', ), numIntervals=1,   
    region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)  
    
#: Job  
mdb.Job(name='GTN_CP', model='GTN_CP', description='', type=ANALYSIS,   
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,   
    memoryUnits=PERCENTAGE, explicitPrecision=DOUBLE_PLUS_PACK,   
    nodalOutputPrecision=FULL, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF,   
    historyPrint=OFF, userSubroutine='', scratch='',   
    parallelizationMethodExplicit=DOMAIN, numDomains=2,   
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=2)  
    
    
#: GENETIC ALGORITHM  
#: Class Creation  
creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))  
creator.create("Individual", list, fitness=creator.FitnessMin)  
#: Toolbox Registration - Population  
Ind_Size = 0  
for i in range(len(nbits)):  
    Ind_Size =  Ind_Size+nbits[i]  
print Ind_Size  
toolbox = base.Toolbox()  
toolbox.register("attr_bool", random.randint, 0, 1)  
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, Ind_Size)  
toolbox.register("population", tools.initRepeat, list, toolbox.individual)  
    
#: Binary convertor  
def bin2float(min_, max_, nbits):      
    def wrap(function):  
        def wrapped_function(individual, *args, **kargs):  
            decoded = [0] * len(nbits)  
            for i in range(len(nbits)):  
                gene = int("".join(map(str, individual[i*nbits[i]:i*nbits[i]+nbits[i]])), 2)  
                div = 2**nbits[i] - 1  
                temp = float(gene)/float(div)  
                decoded[i] = min_[i] + (temp * (max_[i] - min_[i]))  
            return function(decoded, *args, **kargs)  
        return wrapped_function  
    return wrap  
#: Function Bin to Dec Convertor  
def parconvert(x):          
    return [x[i] for i in range(len(nbits))]  
    
    
#: Evaluation  
    
TEMP_IND = TEMP_oper1 = TEMP_oper2 = []  
    
def evaluateInd(individual):  
        
    global TEMP_IND  
    global TEMP_oper1  
    global TEMP_oper2  
    VERDADE = False  
    
    
    cont=0  
    while True:  
        try:  
            cont+=1  
            print "Tentativa"+str(cont)  
#            if cont>10:  
#                mdb.jobs['GTN_CP'].waitForCompletion()                  
#                continue   
        
            for i in range(len(TEMP_IND)):  
                if individual == TEMP_IND[i]:  
                    TEMP_i = i              
                    VERDADE = True  
                        
            if VERDADE == True:    
                print 'Repetido'  
                oper1 = TEMP_oper1[TEMP_i]  
                oper2 = TEMP_oper2[TEMP_i]  
                    
            else:      
                #: Calculo New Fitness  
                            
                #Parameters  
                Parameter=(bin2float(min_, max_, nbits)(parconvert)(individual))  
                print "ParÃ¢metro:"  
                print Parameter  
                        
                q1 = 1.5  
                q2 = 1  
                F0 = Parameter[0]      
                Ff = Parameter[1]  
                Fc = Parameter[2]  
                Fn = Parameter[3]  
                En = Parameter[4]  
                Sn = Parameter[5]  
                    
                if Fc>Ff:  
                    print 'Invalid Parameter Fc ='+str(Fc)+''''' 
                    '''            
                elif Fn>Fc:  
                    print 'Invalid Parameters Fn ='+str(Fn)+''''' 
                    '''  
                elif Sn>En/2.337:  
                    print 'Invalid Parameters Sn ='+str(Sn)+''''' 
                    '''  
                else:   
    
                    mdb.models['GTN_CP'].materials['STEEL'].PorousMetalPlasticity(relativeDensity = F0, table=((q1, q2, q1**2), ))  
                    mdb.models['GTN_CP'].materials['STEEL'].porousMetalPlasticity.PorousFailureCriteria(fraction = Ff, criticalFraction = Fc)  
                    mdb.models['GTN_CP'].materials['STEEL'].porousMetalPlasticity.VoidNucleation(table=((En, Sn, Fn), ))  
                
                    #: Running Analysis  
                    mdb.jobs['GTN_CP'].submit(consistencyChecking=OFF)  
                    mdb.jobs['GTN_CP'].waitForCompletion()   
                    #: Running Analysis END  
                        
                    #: Output Database      
                    o3 = session.openOdb(name='C:/Temp/GTN_CP.odb')  
                
                    #: RF Data  
                    odb = session.odbs['C:/Temp/GTN_CP.odb']  
                    xy0 = session.XYDataFromHistory(name='RF-1', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 3 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy1 = session.XYDataFromHistory(name='RF-2', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 4 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy2 = session.XYDataFromHistory(name='RF-3', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 49 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy3 = session.XYDataFromHistory(name='RF-4', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 50 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy4 = session.XYDataFromHistory(name='RF-5', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 51 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy5 = session.XYDataFromHistory(name='RF-6', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 52 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy6 = session.XYDataFromHistory(name='RF-7', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 53 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy7 = session.XYDataFromHistory(name='RF-8', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 54 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy8 = session.XYDataFromHistory(name='RF-9', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 55 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy9 = session.XYDataFromHistory(name='RF-10', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 56 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy10 = session.XYDataFromHistory(name='RF-11', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 57 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy11 = session.XYDataFromHistory(name='RF-12', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 58 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy12 = session.XYDataFromHistory(name='RF-13', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 59 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy13 = session.XYDataFromHistory(name='RF-14', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 60 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy14 = session.XYDataFromHistory(name='RF-15', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 61 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy15 = session.XYDataFromHistory(name='RF-16', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 62 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy16 = session.XYDataFromHistory(name='RF-17', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 63 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy17 = session.XYDataFromHistory(name='RF-18', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 64 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy18 = session.XYDataFromHistory(name='RF-19', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 65 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy19 = session.XYDataFromHistory(name='RF-20', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 66 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy20 = session.XYDataFromHistory(name='RF-21', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 67 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy21 = session.XYDataFromHistory(name='RF-22', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 68 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy22 = session.XYDataFromHistory(name='RF-23', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 69 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy23 = session.XYDataFromHistory(name='RF-24', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 70 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy24 = session.XYDataFromHistory(name='RF-25', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 71 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy25 = session.XYDataFromHistory(name='RF-26', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 72 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy26 = session.XYDataFromHistory(name='RF-27', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 73 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy27 = session.XYDataFromHistory(name='RF-28', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 74 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy28 = session.XYDataFromHistory(name='RF-29', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 75 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy29 = session.XYDataFromHistory(name='RF-30', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 76 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy30 = session.XYDataFromHistory(name='RF-31', odb=odb,   
                        outputVariableName='Reaction force: RF2 at Node 77 in NSET TOP', steps=(  
                        'Step-1', ), )  
                    xy31 = sum((xy0, xy1, xy2, xy3, xy4, xy5, xy6, xy7, xy8, xy9, xy10, xy11, xy12,   
                        xy13, xy14, xy15, xy16, xy17, xy18, xy19, xy20, xy21, xy22, xy23, xy24,   
                        xy25, xy26, xy27, xy28, xy29, xy30, ), )  
                
                    #: U Data  
                    xy32 = session.XYDataFromHistory(name='U', odb=odb,   
                        outputVariableName='Spatial displacement: U2 at Node 3 in NSET NO-U',   
                        steps=('Step-1', ), )  
                
                    #: UxRF Data  
                    xy33 = combine(xy32, xy31)  
                
                    tmpName = xy31.name  
                    session.xyDataObjects.changeKey(tmpName, 'RF')  
                    tmpName = xy33.name  
                    session.xyDataObjects.changeKey(tmpName, 'UxRF-GTN_CP')  
                
                    #: NECK  
                    odb = session.odbs['C:/Temp/GTN_CP.odb']  
                    session.XYDataFromHistory(name='NECK', odb=odb,   
                        outputVariableName='Coordinates: COOR1 at Node 149 in NSET NO-NECK',   
                        steps=('Step-1', ), )  
                
                    #: Saving Data  
                    x0 = session.xyDataObjects['UxRF-GTN_CP']  
                    session.writeXYReport(fileName='GTN-RF.txt', appendMode=OFF, xyData=(x0, ))  
                    x1 = session.xyDataObjects['NECK']  
                    session.writeXYReport(fileName='GTN-NECK.txt', appendMode=OFF, xyData=(x1, ))  
                
                    #: Deleting All Data  
                    for i in range(31):  
                        del session.xyDataObjects['RF-'+str(i+1)]  
                
                    del session.xyDataObjects['RF']  
                    del session.xyDataObjects['U']  
                    del session.xyDataObjects['NECK']  
                    del session.xyDataObjects['UxRF-GTN_CP']  
        
                    session.odbs['C:/Temp/GTN_CP.odb'].close()      
                    #: ODB END  
                                
                #: Avaliating Results  
                if Fc>Ff:  
                    oper1 = oper2 = 1  
                elif Fn>Fc:  
                    oper1 = oper2 = 1  
                elif Sn>En/2.337:  
                    oper1 = oper2 = 1  
                else:  
                    oper0 = [0]*NumPT  
                    oper1 = oper2 = 0  
                    data0,data1 = np.genfromtxt('C:\\temp\\GTN-RF.txt', skip_header=2, unpack=True)  
                    for i in range(len(data1)):  
                        if data1[i] < 0:  
                            data1[i:] = 0  
                    for i in range(len(data1)):  
                        if data[i] == 0:  
                            oper0[i] = 0  
                        else:  
                            oper0[i] = ((data1[i]-data[i])/data[i])**2.  
                    oper1 = (sum(oper0)/len(data1))**0.5  
                        
                    NECK0,NECK1 = np.genfromtxt('C:\\temp\\GTN-NECK.txt', skip_header=2, unpack=True)  
                    oper2 = ((NECK-NECK1[1])**2)**0.5/NECK     
                #: Calculo New Fitness Final  
                    
                #: New TEMP  
                TAMANHO = len(TEMP_IND)+1  
                TEMP_IND2 = [0] * TAMANHO  
                TEMP_oper1_2 = [0] * TAMANHO  
                TEMP_oper2_2 = [0] * TAMANHO  
                    
                for j in range(len(TEMP_IND)):  
                    TEMP_IND2[j] = TEMP_IND[j]  
                    TEMP_oper1_2[j] = TEMP_oper1[j]  
                    TEMP_oper2_2[j] = TEMP_oper2[j]  
                    
                TEMP_IND2[len(TEMP_IND2)-1] = individual  
                TEMP_oper1_2[len(TEMP_oper1_2)-1] = oper1  
                TEMP_oper2_2[len(TEMP_oper2_2)-1] = oper2  
                    
                TEMP_IND = TEMP_IND2  
                TEMP_oper1 = TEMP_oper1_2  
                TEMP_oper2 = TEMP_oper2_2                  
                #: New TEMP Final  
        except:  
            continue  
        break          
            
    print "Fitness1 = "+str(oper1)+" Fitness2 = "+str(oper2)+''''' 
    '''  
    return oper1, oper2  
    
    
#: Toolbox Registration - Operetor Set  
toolbox.register("mate", tools.cxTwoPoint)  
toolbox.register("mutate", tools.mutFlipBit, indpb=IndPB)  
toolbox.register("select", tools.selTournament, tournsize=Tournament)  
toolbox.register("evaluate", evaluateInd)  
    
#: Algorithm  
def main():  
    pop = toolbox.population(Pop_Size)  
    hof = tools.HallOfFame(nglobal_max)  
    stats = tools.Statistics(lambda ind: ind.fitness.values)  
    stats.register("avg", np.mean, axis=0)  
    stats.register("min", np.min, axis=0)  
    stats.register("max", np.max, axis=0)  
    pop, logbook = algorithms.eaSimple(pop, toolbox, CXPB, MutPB, NGen, stats=stats, halloffame=hof, verbose=True)  
    return pop, logbook, hof  
if __name__ == "__main__":  
    pop, log, hof = main()  
    print(" ")  
    result=[0]*nglobal_max  
    for glob in range(nglobal_max):  
        HallFame = bin2float(min_, max_, nbits)(parconvert)(hof[glob])  
        hofFit = hof[glob].fitness          
        print"Global minimum "+str(1+glob)+" is: %s \nwith fitness: %s" % (HallFame, hofFit,)          
        result[glob]=((HallFame))  
    np.savetxt('C:\\temp\\GTN-GA_Result.txt', result, fmt='%f', delimiter=',')  
    print("END")
