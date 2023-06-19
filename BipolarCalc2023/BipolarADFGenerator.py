import random,string, functools,os
import datetime
from pathlib import Path

## script for generating bipolar ADF models

# prefix for storing the models in the specified directory
directoryPrefix = "BipolarADF_StatementSize_"
# store all models additionally in one file, so it
modelTotalStore = "BipolarADFAllDataControl.txt"
# set seed for reproducibility
random.seed(2)

# class for generating ADF models
# nbr_statements is the desired statement size of the ADF, max 26 statements can be used, according to letters of the alphabet
class BipolarFormulaGenerator():
    def __init__(self, nbr_statements):
        self.nbrStatements = nbr_statements
        self.statements = [string.ascii_lowercase[x] for x in range(0, self.nbrStatements)] # create list of available statements
        # set maximal number of possible disjuncts in an acceptance condition, standard is that all nodes can be used
        self.nbrDisjunctionMax = nbr_statements

    # select statements which shall be used in the acceptance condition of a statement
    def acceptance_condition_statement_selector(self):
        statementList = []
        for statement in self.statements:
            decisionTest = random.randint(1, 2)
            if (decisionTest == 1): # statement is selected
                representation = statement
                negationTest = random.randint(1, 2)
                if (negationTest == 1): # we take negation of statement
                    representation = "#" + statement
                statementList.append(representation)
        return statementList

    # create the acceptance condition for a single statement
    def acceptance_condition_generator(self):
        # get list of used statements in the acceptance condition
        selectedStatementsList = self.acceptance_condition_statement_selector()
        nbrConjunctionMax = len(selectedStatementsList) # maximum number of nodes in a conjunct, which are all available statements
        # intermediate storage for used disjuncts
        AcceptanceConditionDisjunctsList = []
        if selectedStatementsList == []: # falsum or verum is used
            gen_nbr = random.randint(1, 2)
            if (gen_nbr == 1):
                return "?"
            else: return "!"

        nbrDisjuncts = random.randint(1, self.nbrDisjunctionMax) # determine number of disjuncts in the acceptance condition
        for x in range(0,nbrDisjuncts):

            # set number of literals in the current conjunct
            nbrCurrentConjunct = random.randint(1,nbrConjunctionMax)

            # select and sort statements
            conjunctNodes = sorted(random.sample(selectedStatementsList,nbrCurrentConjunct))

            conjunctNodesSyntaxStyle = functools.reduce(lambda x, y: "({},{})".format(x, y), conjunctNodes)

            AcceptanceConditionDisjunctsList.append(conjunctNodesSyntaxStyle)

        statementAcceptanceCondition = functools.reduce(lambda x, y: "({};{})".format(x, y), AcceptanceConditionDisjunctsList)
        return statementAcceptanceCondition

    # create a single ADF model
    def model_creator(self):
        finalStatementsAcceptanceConditions = []
        for statement in self.statements:
            acceptcond = self.acceptance_condition_generator()
            finalStatementsAcceptanceConditions.append([statement,acceptcond])
        return finalStatementsAcceptanceConditions


# create models for an ADF with a specified statement size
# nbr_instances specifies the number of models which shall be created,
# nbr_files specifies number of data files which shall be created total
# therefore number of models in a file (model size) equals number of desired total models (nbr_instances) divided through number of desired files (nbr_files)
class CreateInstances():
    def __init__(self, statement_size, nbr_instances, nbr_files):
        # internal dictionary for storing formula
        self.statementSize = statement_size
        self.statementNamesAlphabet = [string.ascii_lowercase[x] for x in range(0, self.statementSize)]

        # this dictionary contains already generated acceptance conditions, is used to prevent duplicates
        self.statement_dict = dict()
        for statement in self.statementNamesAlphabet:
            self.statement_dict.update({statement : dict()})

        self.nbrInstancesTotal = nbr_instances
        self.nbrFilesTotal = nbr_files
        self.sizeSingleFile = int(self.nbrInstancesTotal / self.nbrFilesTotal)
        self.timestempId = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # paths which are specifiyng where the generated models shall be stored and where the dataControlFile is located
        self.filePathDataStorage = Path.joinpath(Path.cwd(), directoryPrefix + str(self.statementSize), "Data/")
        self.filePathDataStorageControl = Path.joinpath(self.filePathDataStorage, modelTotalStore)

        self.totalModels = []
        #  check that all created files have the same size, if not abort
        if self.nbrInstancesTotal % self.sizeSingleFile != 0:
            print("Check Model Number or Size of Single File - Aborting")
            return

        self.nbrDoubleInstances = 0
        self.nbrGeneratedInstances = 0
        self.generatedModelList = []


    # reset parameters to check for new combination
    def create_data_files(self):
        biPolarGen = BipolarFormulaGenerator(self.statementSize)

        nbrID = 0 # indicator for the current number of files used
        # check if models have already been generated before
        if self.filePathDataStorageControl.exists():
            with open(self.filePathDataStorageControl, "r") as totalModels:
                for line in totalModels:
                    evalModel = eval(line.replace("Model:",""))
                    self.initate_checklist(evalModel)
                    nbrID += 1

        for nbr in range(1, self.nbrFilesTotal + 1):
            # generate instances and sort out duplicates
            while self.nbrGeneratedInstances != self.sizeSingleFile:
                generatedModel = biPolarGen.model_creator()
                # append new models to the internal storage
                self.check_instance(generatedModel)

            fileIDNbr = nbr + nbrID
            # file name for storage
            filename = "BipolarADFTest_TimestempID_{}_StatementNbr_{}_ModelSize_{}_IDNbr_{}_Data.txt".format(
                self.timestempId,self.statementSize,self.sizeSingleFile, fileIDNbr)

            # create path for storage if required
            if self.filePathDataStorage.exists() == False:
                Path.mkdir(self.filePathDataStorage,parents=True)

            fileNamePath = Path.joinpath(self.filePathDataStorage,filename)
            instance_file = open(fileNamePath, "w")
            control_File = open(self.filePathDataStorageControl,"a")

            for model in self.generatedModelList:
                content = "Model:"+ str(model) + "\n"
                instance_file.write(content)
                control_File.write(content)
            instance_file.close()
            control_File.close()

            # reset list of generated instances
            self.generatedModelList = []
            self.nbrGeneratedInstances = 0
        print("Double Size{} Nbr{}".format(self.statementSize, self.nbrDoubleInstances))

    # create a checklist for better and more generation of data
    def initate_checklist(self, single_model):
        for statement_statementAcceptCond in single_model: # go through statements and acceptance conditions
            # create empty check list
            current_used_formulae_dict = self.statement_dict[statement_statementAcceptCond[0]] # get already used acceptance conditions for a statement
            formula_key = str(statement_statementAcceptCond[1])  # representation of the acceptance condition
            # use acceptance condition as key
            current_used_formulae_dict.update({formula_key : True})

    # check if a created model has been generated before
    def check_instance(self, single_model):
        nbr_of_statements = len(single_model)
        check_list = []  # if an acceptance condition already exists it is notated in the list

        for statement_statementAcceptCond in single_model: # go through statements and acceptance conditions
            # create empty check list
            current_used_formulae_dict = self.statement_dict[statement_statementAcceptCond[0]] # get already used acceptance conditions for a statement
            formula_key = str(statement_statementAcceptCond[1])  # representation of the acceptance condition
            if nbr_of_statements >= 3 and formula_key in current_used_formulae_dict: # check if the formula key has been already used as acceptance condition for the statement
                check_list.append(1)
            else:
                #  mark that the acceptance condition of the statement has been used before
                current_used_formulae_dict.update({formula_key : True})

        if len(check_list) == nbr_of_statements: # all acceptance conditions in the model are already existing, therefore the generated model is skipped
            self.nbrDoubleInstances += 1
        else:
            self.nbrGeneratedInstances += 1
            # add model to final list
            self.generatedModelList.append(single_model)


# each file should only contain one statement, this way easier handling is possible

# for each statement size ranging from 1 to 9 create 100 models; the data is distributed to 5 files for each statement size
def generate_data():
    for x in range(1,15+1):
        CreateInstances(x, 100, 100).create_data_files()
generate_data()








