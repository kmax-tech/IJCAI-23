import re
import matplotlib
import matplotlib.pyplot as plt, numpy as np
from pathlib import Path

## script in order to analyze the previously calculated data
matplotlib.use('Qt5Agg')


workingDirectoryPath = Path.joinpath(Path.cwd())
# check for directory name
statementSizeDirectory = "BipolarADF_StatementSize_"


# for a specified statement size and semantics retrieve all results and determine average time for the calculation of one model
# time is determined for the two calculation styles of two-valued completion and three-valued logic approach

class SemanticsCalcStyleRetriever():
    def __init__(self,semantics,calcStyle):

        # min and max size for statements sizes under consideration
        self.minSize = 1
        self.maxSize = 12

        self.semantics = "".join(semantics)
        self.calcStyle = calcStyle
        self.modelDescription = "Sem_{}_CalcStyle_{}".format(self.semantics,self.calcStyle)
        self.currentStatementSize = None # used for retrieving specified statement size

        self.statemenSizeModelsTimeResultsDict = dict()
        # for checking that models have the same result
        self.statementSizeIDNbrModelsTimeResultsDict = dict() # entries sorted according to File ID numbers
        # for storing calculation time for the distinct statement sizes
        self.statementSizeTimeDict = dict()
        # storing mean calculation time for statement sizes
        self.StatementSizeTimeMeanDict = dict()

        self.get_results_semantics_calcStyle()
        self.get_calculationTime_one_run()
        self.calculate_mean_calculation_one_run()

    # for specified semantics and calculation style retrieve all calculated models, results and calculation time
    def get_results_semantics_calcStyle(self):
        # go through working directory, find directories containing data
        for entry in workingDirectoryPath.iterdir():
            if statementSizeDirectory in entry.name: # we found a directory containing data
                # retrieve the current statementSize
                statementSize = re.findall(r"_StatementSize_(\d+)", entry.name)
                self.currentStatementSize = statementSize[0]
                # check if retrieved statement size shall be processed
                if self.minSize <= int(self.currentStatementSize) <= self.maxSize:
                    # path for finding the evaluated model:
                    pathEvaluatedModels = Path.joinpath(workingDirectoryPath,entry.name,self.modelDescription)
                    if pathEvaluatedModels.exists():
                        modelsList,timeResultsList,idNumberDict = self.get_evaluated_models_semantics_time_directory(
                            pathEvaluatedModels)
                        self.statemenSizeModelsTimeResultsDict.update({self.currentStatementSize : [modelsList, timeResultsList]})
                        # if id number was retrieved
                        if len(idNumberDict) != 0:
                            self.statementSizeIDNbrModelsTimeResultsDict.update({self.currentStatementSize:idNumberDict})


    def get_evaluated_models_semantics_time_directory(self, modelPath):
        # retrieved eval files should contain the correct statement size
        modelRegExprRaw = r"Eval.*StatementNbr_" + str(self.currentStatementSize) + "_.*" + self.modelDescription
        modelRegExpr = re.compile(modelRegExprRaw)
        modelRegExprIDNumber = re.compile("_IDNbr_(\d+)_")
        idNumberDict = dict()
        modelsList = []
        timeResultsList = []
        for modelFilePath in modelPath.iterdir():
            if modelRegExpr.search(modelFilePath.name):
                modelIDNbr = re.findall(modelRegExprIDNumber,modelFilePath.name)

                models,timeResults = self.retrieve_models_semantics_file(modelFilePath)
                modelsList += models
                timeResultsList += timeResults

                # if modelIDNbr could be retrieved extract used data
                if modelIDNbr != []:
                    idNumberDict.update({modelIDNbr[0]:[models,timeResults]})

        return modelsList,timeResultsList,idNumberDict

    # get the needed calculation time for the first run
    def get_calculationTime_one_run(self):
        for statementSize in self.statemenSizeModelsTimeResultsDict:
            timeStatementSizeList = []
            ModelsSemanticsTimeResultsList = self.statemenSizeModelsTimeResultsDict[statementSize]
            # go through with semantics and calculation time and retrieve calculation time
            for SemanticsTimeResults in ModelsSemanticsTimeResultsList[1]:
                # append only calculation time [0] from first run [0]
                timeStatementSizeList.append(SemanticsTimeResults[0][0])
            self.statementSizeTimeDict.update({statementSize : timeStatementSizeList})

    # calculate mean of first run
    def calculate_mean_calculation_one_run(self):
        for statementSize in self.statementSizeTimeDict:
            timeList = self.statementSizeTimeDict[statementSize]
            regexTimeout = re.compile("Timeout")
            timeOutCounter = 0
            calcTime = []
            # remove all entries where timeout occurred or which where not calculated

            # at this point average calculation could be implemented, if multiple measurements are done
            for timeEntry in timeList:
               # if isinstance(timeEntry,float) == False:
                    # print("Unusual Occurrence",timeEntry)
                if regexTimeout.search(str(timeEntry)):
                    timeOutCounter += 1
                    continue
                else:
                    calcTime.append(timeEntry)

            calculatedMean = None
            if timeOutCounter >= 3:
                calculatedMean = "Timeout"
            else:
                # calculate mean of results
                calculatedMean = np.mean(calcTime)
            self.StatementSizeTimeMeanDict.update({statementSize:calculatedMean})


    # retrieve calculation time from evaluated data for specific statement size and store results in a lists, filename is specified by regexpr
    def retrieve_models_semantics_file(self, modelPath):
        models = []
        timeResults = []
        with open(modelPath,"r") as calc_results:
            for line in calc_results:
                if line.startswith("#"): # filter out comments
                    continue
                if line.startswith("Model"):
                    models.append(eval(line.replace("Model:", "")))
                if line.startswith("Semantics:"):
                    evaluated = eval(line.replace("Semantics:", ""))
                    timeResults.append(evaluated)
        return models,timeResults

    def print_info(self):
        for statementSize in sorted(self.statementSizeIDNbrModelsTimeResultsDict):
            print(statementSize)
            TimeModels = self.statemenSizeModelsTimeResultsDict[statementSize][1]
            for TimeSemantics in TimeModels:
                lenghtOfInstances = []
                for semantic in TimeSemantics[0][1]: # take first run and semantics
                    lenghtOfInstances.append(len(semantic))
                print(lenghtOfInstances)



    # values which are being used for checking

adm = SemanticsCalcStyleRetriever(["a"],"twoValOpt")
adm.print_info()
admTri = SemanticsCalcStyleRetriever(["a"],"tri")
cmp = SemanticsCalcStyleRetriever(["c"],"twoValOpt")
cmpTri = SemanticsCalcStyleRetriever(["c"],"tri")
prf = SemanticsCalcStyleRetriever(["p"],"twoValOpt")
prfTri = SemanticsCalcStyleRetriever(["p"],"tri")
#prfTri.print_info()

#compare two data objects

class optimizedValueChecker():
    def __init__(self,calcObjectA,calcObjectB):
        self.semanticOrder = ["adm","cmp","prf","grd"]
        self.calcResultsObjectA = calcObjectA.statementSizeIDNbrModelsTimeResultsDict
        self.calcResultsObjectB = calcObjectB.statementSizeIDNbrModelsTimeResultsDict

        self.check_semantics_one_run()

    # we only look at the instances we have calculated before
    def check_semantics_one_run(self):
        for statementSize in self.calcResultsObjectA:
            # check if the statement size was caluclated before
            if statementSize not in self.calcResultsObjectB:
                print("StatementSize does not exist in both objects",statementSize)
                continue
            evaluatedInstancesStatementSizeA = self.calcResultsObjectA[statementSize]
            evaluatedInstancesStatementSizeB = self.calcResultsObjectB[statementSize]

            for iDNbrCalculatedInstance in evaluatedInstancesStatementSizeA:
                if iDNbrCalculatedInstance not in evaluatedInstancesStatementSizeB:
                    print("IDNbr not found",iDNbrCalculatedInstance)
                    continue

                # retrieve data for IDNbr
                modelsInstanceA = evaluatedInstancesStatementSizeA[iDNbrCalculatedInstance][1]
                modelsInstanceB = evaluatedInstancesStatementSizeB[iDNbrCalculatedInstance][1]
                # translate if necessary
                modelsInstanceATranslated = self.translate_grammar(modelsInstanceA[0][0][1])
                modelsInstanceBTranslated = self.translate_grammar(modelsInstanceB[0][0][1])

                self.check_instances(modelsInstanceATranslated,modelsInstanceBTranslated)

    # compare instances, each instance contains list, where each entry resembles a semantics, containing multiple interpretations
    def check_instances(self,instancesA,instancesB):
        errorList = []
        if isinstance(instancesA,str) or isinstance(instancesB,str): # abort in of error or timeout
            return

        for ind,interpretationsSingleSemanticsA in enumerate(instancesA):
            if len(interpretationsSingleSemanticsA) > 0:
                intpretationsSingleSemanticsB = instancesB[ind]
                for singleInterpretationInstanceA in interpretationsSingleSemanticsA:
                    # cycle through the list and check if the interpretation appears in each list
                        if singleInterpretationInstanceA in intpretationsSingleSemanticsB:
                            continue
                        else:
                            errorList.append(["Instance Error:{}".format(singleInterpretationInstanceA),"InterpretationList1:{}".format(interpretationsSingleSemanticsA),"InterpretationList2:{}".format(intpretationsSingleSemanticsB)])
        if errorList == []:
            pass
            #print("Everything Okay")
        else:
            print("Error",errorList)

    # translate three-valued logic ti
    def translate_grammar(self,semanticsModelList):
        if isinstance(semanticsModelList,str): # skype in case of timeout
            return semanticsModelList
        translatedSemanticsModelList = []
        # dictionary used to translate output of three-valued logic to output of two-valued completion
        translateDictReference = {'1.0':'True','0.5':'u','0.0':'False'}
        for interpretationsSingleSemanticsList in semanticsModelList:
            translatedInterpretationsSingleSemantic = []
            for interpretation in interpretationsSingleSemanticsList:
                translatedInterpretation = dict()
                for node,value in interpretation.items():
                    if value in translateDictReference.keys():
                        value = translateDictReference[value]
                    translatedInterpretation.update({node:value})
                translatedInterpretationsSingleSemantic.append(translatedInterpretation)
            translatedSemanticsModelList.append(translatedInterpretationsSingleSemantic)
        return translatedSemanticsModelList

# check if calculated instances between the calculation approaches are the same
admCheck = optimizedValueChecker(adm,admTri)
#cmpCheck = optimizedValueChecker(cmp,cmpTri)
#prfCheck = optimizedValueChecker(prf,prfTri)

# pair the calculation object, with two different calculation styles, for same semantics
# semanticsNameDescription specifies the used semantics in the legend
def group_statements(calcObjectTwoVal, calcObjectTriVal, semanticsNameDescription):
    semanticsNameDescription = semanticsNameDescription
    returnStatementSize = []
    returnTwoValuedApproach = []
    returnThreeValuedApproach = []
    # access dictionaries containing the mean
    twoValMeanDict = calcObjectTwoVal.StatementSizeTimeMeanDict
    triValMeanDict = calcObjectTriVal.StatementSizeTimeMeanDict

    # timeouts shall not be displayed in the graph, but in the table, therefore we notate indices so timeout entries can be sorted out
    twoValNoDisplayInd = []
    triValNiDisplayInd = []
    # sort statements according to size
    sortedSize = sorted(list(map(lambda x: int(x), twoValMeanDict.keys())))
    for ind,size in enumerate(sortedSize):
        resultTwoValuedCalculation = twoValMeanDict[str(size)]
        resultThreeValuedCalculation = triValMeanDict[str(size)]
        # check if errors occurred
        if isinstance(resultTwoValuedCalculation,str):
            twoValNoDisplayInd.append(ind)

        if isinstance(resultThreeValuedCalculation,str):
            triValNiDisplayInd.append(ind)

        returnStatementSize.append(size)
        returnTwoValuedApproach.append(resultTwoValuedCalculation)
        returnThreeValuedApproach.append(resultThreeValuedCalculation)
    return semanticsNameDescription,returnStatementSize,returnTwoValuedApproach,returnThreeValuedApproach,twoValNoDisplayInd,triValNiDisplayInd
admPair = group_statements(adm, admTri, "adm")
cmpPair = group_statements(cmp, cmpTri, "cmp")
prfPair = group_statements(prf, prfTri, "prf")

sigmaPair = group_statements(adm, admTri, "σ")


# a function that returns True if a statement size is not blocked
def filter_statements(list,listIndicesProhibited):
    finalList = []
    for ind,entry in enumerate(list):
        if ind in listIndicesProhibited:
            continue
        finalList.append(entry)
    return  finalList

# for specified calculation pairs plot the average time for the two and three-valued style
def plot_gain(comparison1,comparison2):
    # collect two and three-valued results for sem1
    statementSizeListTwoVal1 = filter_statements(comparison1[1],comparison1[4])
    statementSizeListTriVal1 = filter_statements(comparison1[1],comparison1[5])

    twoValuedCompletionList1 = filter_statements(comparison1[2],comparison1[4])
    triValuedCompletionList1 = filter_statements(comparison1[3],comparison1[5])
    sem1note = comparison1[0]

    # collect two and three-valued results for sem2
    statementSizeListTwoVal2 = filter_statements(comparison2[1],comparison2[4])
    statementSizeListTriVal2 = filter_statements(comparison2[1],comparison2[5])
    twoValuedCompletionList2 = filter_statements(comparison2[2],comparison2[4])
    triValuedCompletionList2 = filter_statements(comparison2[3],comparison2[5])
    sem2note = comparison2[0]

    # create a plot
    font = {'family': 'serif',
            'weight': 'normal',
            'size': 14}

    plt.rc('font', **font)
    fig, ax = plt.subplots()

    ax.plot(statementSizeListTwoVal1, twoValuedCompletionList1, label=sem1note + "-two", linewidth=3, color ="b", linestyle="-")
    ax.plot(statementSizeListTriVal1,triValuedCompletionList1, label=sem1note + "-tri", linewidth=3, color ="r", linestyle="-")
    #ax.plot(statementSizeListTwoVal2,twoValuedCompletionList2,label= sem2note +"-two",linewidth=3,color ="r", linestyle="-")
    #ax.plot(statementSizeListTriVal2,triValuedCompletionList2,label=sem2note +"-tri",linewidth=3,color ="r",linestyle="dotted")

    ax.set_ylabel('Time in Seconds',fontsize="medium")
    ax.set_xlabel('Number of Statements',fontsize="medium")
    ax.set_aspect('equal', adjustable='box')
    plt.yscale("log")
    plt.legend(loc='best')
    ax.legend(loc='upper left')
    fig.tight_layout()
    # ax.yaxis(fontsize="medium")
    ax.set_xlim(xmin=1, xmax=len(statementSizeListTwoVal1))
    plt.xticks(statementSizeListTwoVal1)
    # ax.set_title('Comparison of Admissible and Complete Semantics',fontsize="medium")
    plt.show()

plot_gain(sigmaPair,prfPair)


# helper in order to collect data which is needed to create a table; collected semantics are specified in the corresponding variable
# for each specified semantics we collect the average time of the two-valued completion and the three-valued logic approach
# in addition we calculate the speed factor, indicating how much faster the latter approach is
# range below specifies which statement size shall be included in the collected data
def tablecontent_creator(pairsSemanticsList):

    # create head
    table_head = ["Size"]
    for singSemPair in pairsSemanticsList:
        semanticsName = singSemPair[0]
        table_head += ["{}".format(semanticsName), "tri-{}".format(semanticsName), "Speed"]

    # get longest number of statement
    maxNumberStatements = max([len(valuePair[1]) for valuePair in pairsSemanticsList])
    final_table = [[] for _ in range(maxNumberStatements)]

    # create body
    for statementSize in range(1,maxNumberStatements+1):
        statementIndex = statementSize - 1
        tableRow = final_table[statementIndex]
        tableRow.append(statementSize)
        for singSemPair in pairsSemanticsList:
            twoTime = singSemPair[2][statementIndex]
            if twoTime == 'Timeout':
                twoTime = "time"

            triTime = singSemPair[3][statementIndex]
            if triTime == 'Timeout':
                triTime = "time"

            if isinstance(twoTime,str) or isinstance(triTime,str):
                speed = "n.a."
            else:
                speed = np.divide(twoTime,triTime)
            tableRow.append([twoTime,triTime,speed])
    return [table_head] + final_table

tableRaw = tablecontent_creator([admPair,cmpPair,prfPair])

# tex style writer for data obtained by tablecontent_creator
def mult_tex_writer(dataTable):
    nbrColumnsDataTable = len(dataTable[0])
    templateRow = r"{}\\"
    dataheadRaw = "{}&" * nbrColumnsDataTable
    dataheadRaw = dataheadRaw[:-1] # remove ampersand
    datahead = dataheadRaw.format(*dataTable[0])
    print("\\begin{tabular}{" + ("c|" * len(dataTable[0]))[:-1] + "}")
    print(templateRow.format(datahead))
    for dataRow in dataTable[1:]:
        dataRowRaw = "{} &" * nbrColumnsDataTable
        dataRowRaw = dataRowRaw[:-1] # remove ampersand
        dataRowValues = []

        # append statementSize, which is first entry of dataRow
        dataRowValues.append((dataRow[0]))

        # go through measurements for approaches, which are being compared
        for dataPair in dataRow[1:]:
            twoTime = dataPair[0]
            triTime = dataPair[1]
            speedFactor = dataPair[2]

            twoTimeStr = str(twoTime)
            triTimeStr = str(triTime)
            speedFactorStr = str(speedFactor)

            if isinstance(twoTime,float):
                twoTime = np.round(twoTime, 4)
                twoTimeStr = "$" + str(twoTime) + "$"
            if isinstance(triTime,float):
                triTime = np.round(triTime, 4)
                triTimeStr = "$" + str(triTime) + "$"
            if isinstance(speedFactor,float):
                speedFactor = np.round(speedFactor,2)
                speedFactorStr = "$" + str(speedFactor) + "$"


            dataRowValues += [twoTimeStr,triTimeStr,speedFactorStr]

        # do formatting
        formated = dataRowRaw.format(*dataRowValues)
        print(templateRow.format(formated))
    print("\\end{tabular}")

mult_tex_writer(tableRaw)

# html style writer for data obtained by tablecontent_creator
def mult_html_writer(dataTable):
    nbrColumnsDataTable = len(dataTable[0])
    templateRow = r"<tr>{}</tr>"
    dataheadRaw = "<th>{}</th>" * nbrColumnsDataTable
    dataheadRow = dataheadRaw.format(*dataTable[0])
    print("<table>")
    print(templateRow.format(dataheadRow))
    for dataRow in dataTable[1:]:
        dataRowRaw = "<td>{}</td>" * nbrColumnsDataTable
        dataRowRaw = dataRowRaw[:-1] # remove ampersand
        dataRowValues = []

        # get statementSize, is first entry of dataRow
        dataRowValues.append((dataRow[0]))

        # go through measurements for approaches, which are being compared
        for dataPair in dataRow[1:]:
            twoTime = dataPair[0]
            triTime = dataPair[1]
            speedFactor = dataPair[2]

            if isinstance(twoTime,float):
                twoTime = np.round(twoTime, 4)
            if isinstance(triTime,float):
                triTime = np.round(triTime, 4)
            if isinstance(speedFactor,float):
                speedFactor = np.round(speedFactor,2)
            dataRowValues += [twoTime,triTime,speedFactor]

        # do formatting
        formated = dataRowRaw.format(*dataRowValues)
        print(templateRow.format(formated))
    print("</table>")

mult_html_writer(tableRaw)



