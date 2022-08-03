import random,string
import datetime
from pathlib import Path

#random.seed(2)
directoryPrefix = "BipolarNodes_"
## BIPOLAR Version

#script for generating testinstances and measuring the time
#class takes as input the length of nodes, max 26 nodes can be used, because letters of the alphabet are used
class BipolarFormula_generator():
    def __init__(self,nbr_nodes):
        self.nbr_nodes = nbr_nodes
        self.nodes = [string.ascii_lowercase[x] for x in range(0,self.nbr_nodes) ]
        self.prob_neg = 0.5
        self.prob_and = 0.5
        # determine number of disjuncts
        # determine number of conjuncts in each disjunct
        self.nbr_dis_max = nbr_nodes

    # specify which node is occuring
    def acceptance_condition_node_selector(self):
        nodelist = []
        for node in self.nodes:
            gen_nbr = random.random()
            if (gen_nbr >= 0.5): #possible that nodelist is empty
                rep = node
                new_nbr = random.random()
                if (new_nbr >= 0.5):
                    rep = "#"+node
                nodelist.append(rep)
        return nodelist

    #create the acceptance condition for a single node
    def acceptance_condition_generator(self):
        # select nodes which are used
        selected_nodes = self.acceptance_condition_node_selector()
        nbr_conMax = len(selected_nodes)
        node_acceptance_condition = ""
        if selected_nodes == []: #contradiction or verum is assumed at this point
            gen_nbr = random.random()
            if (gen_nbr >= 0.5):
                return "?"
            else: return "!"

        # number of disjuncts
        nbr_disjuncts = random.randint(1,self.nbr_dis_max)
        for x in range(0,nbr_disjuncts):
            nbr_current_conjunct = random.randint(1,nbr_conMax)
            nodes_conjunct = random.sample(selected_nodes,nbr_current_conjunct)
            nodes_conjunct ="(" + ",".join(nodes_conjunct) + ")"
            node_acceptance_condition += nodes_conjunct + ";"
        return node_acceptance_condition[:-1] #take out the last connective

    def model_creator(self):
        finalnodes_with_acceptancecondition = []
        for node in self.nodes:
            acceptcond = self.acceptance_condition_generator()
            finalnodes_with_acceptancecondition.append([node,acceptcond])
        return finalnodes_with_acceptancecondition


# create testCases and remove duplicates
class Create_Instances():
    # input list of filenames, the total nbr of models which shall be generated and the nbr each file should contain
    def __init__(self,nbr_nodes,nbr_instances,nbr_files):
        # internal variables dictionary for storing formula
        self.nbr_nodes = nbr_nodes
        self.node_names_alphabet = [string.ascii_lowercase[x] for x in range(0,self.nbr_nodes) ]

        self.node_dict = dict()
        for node in self.node_names_alphabet:
            self.node_dict.update({node : dict()})

        self.nbr_instances_total = nbr_instances
        self.nbr_files_total = nbr_files
        self.size_sing_file = int(self.nbr_instances_total/self.nbr_files_total)
        self.data_id = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

        #  check that all created files have the same size
        if self.nbr_instances_total % self.size_sing_file != 0:
            print("Check Model Number or Size of Single File - Aborting")
            return

        self.nbr_of_doubled_instances = 0
        self.generated_instance_nbr = 0
        self.generated_list = []


    # reset parameters to check for new combination
    def create_data_files(self):
        biPolarGen = BipolarFormula_generator(self.nbr_nodes)
        for nbr in range(0,self.nbr_files_total):

            # generate instances and check for duplicates
            while self.generated_instance_nbr != self.size_sing_file:
                generatedModel = biPolarGen.model_creator()
                # append new models to the internal storage
                self.check_instance(generatedModel)
            #write list to filename
            filename = "BipolarTest_ID_{}_Nodes_{}_ModelNbr_{}_Nbr_{}_Data.txt".format(
                self.data_id,self.nbr_nodes,self.size_sing_file, nbr + 1)

            filePath = Path.joinpath(Path.cwd() ,directoryPrefix + str(self.nbr_nodes))
            # create Path if required
            if filePath.exists() == False:
                Path.mkdir(filePath)
            fileNamePath = Path.joinpath(filePath,filename)
            instance_file = open(fileNamePath, "w")
            for model in self.generated_list:
                instance_file.write("Model:"+ str(model) + "\n" )
            instance_file.close()

            #reset list of generated instances
            self.generated_list = []
            self.generated_instance_nbr = 0
        print("Double",self.nbr_nodes,self.nbr_of_doubled_instances)


    def check_instance(self, single_model):
        nbr_of_nodes = len(single_model)  # first entry of nodes with acceptance condition
        check_list = []  # if an acceptance condition already exists it is notated in the list

        for ind,node_nodeAcceptCond in enumerate(single_model): # go through the node encodings
            # create empty check list
            current_used_formulae_dict = self.node_dict[node_nodeAcceptCond[0]] # get already used acceptance conditions for a node
            formula_key = str(node_nodeAcceptCond[1])
            if nbr_of_nodes >= 3 and formula_key in current_used_formulae_dict: # check if the dict has the current acceptance condition
                check_list.append(1)
            else:
                #  mark that the acceptance condition of the node has been specified before
                current_used_formulae_dict.update({formula_key : True})

        if len(check_list) == nbr_of_nodes: # all instances are already existing
            self.nbr_of_doubled_instances += 1
        else:
            self.generated_instance_nbr += 1
            # add model to final list
            self.generated_list.append(single_model)

def generate_data():
    for x in range(1,10):
        Create_Instances(x,100,5).create_data_files()
generate_data()








