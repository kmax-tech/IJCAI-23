import re

import matplotlib.pyplot as plt, numpy as np
from pathlib import Path

# load required files
#load and get averaged file
def get_results(nodesize,semantics):
    proxy_expr = r"Eval.*Nodes_"+str(nodesize) + "_"
    # do not load tri evaluation
    class_expr = proxy_expr + r".*Sem_(?!.*tri).*" +  ",".join(semantics)
    class_expr = re.compile(class_expr)
    # load tri evaluation
    tri_expr = proxy_expr + r".*Sem_(?=.*tri).*"  +  ",".join(semantics)
    tri_expr = re.compile(tri_expr)
    class_models = retrieveVal(nodesize,class_expr)
    tri_models = retrieveVal(nodesize,tri_expr)

    # do division according to the NodeSize
    a = np.array(class_models)
    class_models_rd = np.divide(np.array(class_models),10)
    tri_models_rd =np.divide(np.array(tri_models),10)

    mclass = np.mean(class_models_rd)
    mtri = np.mean(tri_models_rd)
    print("Info about Length",nodesize,semantics)
    print(len(class_models),mclass)
    print(len(tri_models),mtri)
    return (nodesize,mclass,mtri)

# retrieve time from calculated data, filename is specified by the regex
def retrieveVal(nodenbr, regexpr):
    path_for_search = Path.joinpath(Path.cwd(),"BipolarNodes_{}".format(nodenbr))
    class_time = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): #filter out comments
                        continue
                    if line.startswith("Model"): #filter out comments
                        continue
                    if line.startswith("Semantics:"):
                        evaluated = eval(line.replace("Semantics:", ""))
                        class_time.append(evaluated[0])
            calc_results.close()
    return class_time

#get_results(6,["a"])
# retrieve time from calculated data, filename is specified by the regex

# check length of models for a distinct nodenbr

def modelCounter(nodenbr,regexpr):
    path_for_search = Path.joinpath(Path.cwd(),"BipolarNodes_{}".format(nodenbr))
    models = []
    for filePathName in path_for_search.iterdir():
        if regexpr.search(filePathName.name):
            with open(filePathName,"r") as calc_results:
                for line in calc_results:
                    if line.startswith("#"): #filter out comments
                        continue
                    if line.startswith("Model"): #filter out comments
                        evaluated = line.replace("Model:", "")
                        models.append(evaluated)
                        continue
                    if line.startswith("Semantics:"):
                        continue
            calc_results.close()
    return (len(models)),(len(set(models)))

# search for duplicates in the calculated models
def countModels(min,max,semantics):
    for nodesize in range(min,max+1):
        proxy_expr = r"Eval.*Nodes_"+str(nodesize) + "_"
        # do not load tri evaluation
        two_expr = proxy_expr + r".*Sem_(?!.*tri).*" +  ",".join(semantics)
        two_expr = re.compile(two_expr)
        twoRes = modelCounter(nodesize,two_expr)

        # load tri evaluation
        tri_expr = proxy_expr + r".*Sem_(?=.*tri).*"  +  ",".join(semantics)
        tri_expr = re.compile(tri_expr)
        triRes = modelCounter(nodesize, tri_expr)
        print("NodeSize: {}".format(nodesize))
        print(twoRes,triRes)

countModels(1,8,["a"])


def plot_gain(min,max,sem1,sem2,sem1note,sem2note):
    # append the speed factor
    sem1_final = []
    for nbrNodes in range(min,max+1):
        result = get_results(nbrNodes, sem1)
        sem1_final.append(result)
    sem_nodes_1 = list(map( lambda  x: x[0],sem1_final))
    class_time_1 = list(map( lambda  x: x[1],sem1_final))
    tri_time_1 = list(map( lambda  x: x[2],sem1_final))

    # append the speed factor
    sem2_final = []
    for nbrNodes in range(min, max + 1):
        result = get_results(nbrNodes, sem2)
        sem2_final.append(result)
    sem_nodes_2 = list(map(lambda x: x[0], sem2_final))
    class_time_2 = list(map(lambda x: x[1], sem2_final))
    tri_time_2 = list(map(lambda x: x[2], sem2_final))

    #create a plot
    font = {'family': 'normal',
            'weight': 'normal',
            'size': 50}

    plt.rc('font', **font)
    fig, ax = plt.subplots()

    ax.plot(sem_nodes_1,class_time_1,label=sem1note+"-two",linewidth=3,color ="b", linestyle="-")
    ax.plot(sem_nodes_1,tri_time_1,label= sem1note + "-tri",linewidth=3,color ="b",linestyle="dotted")
    ax.plot(sem_nodes_2,class_time_2,label= sem2note +"-two",linewidth=3,color ="r", linestyle="-")
    ax.plot(sem_nodes_2,tri_time_2,label=sem2note+"-tri",linewidth=3,color ="r",linestyle="dotted")

    ax.set_ylabel('Time in Seconds',fontsize="medium")
    ax.set_xlabel('Number of Statements',fontsize="medium")
    ax.set_aspect('equal', adjustable='box')
    plt.yscale("log")
    plt.legend(loc='best')
    ax.legend(loc='upper left')
    fig.tight_layout()
    #ax.yaxis(fontsize="medium")
    ax.set_xlim(xmin=1, xmax=len(sem_nodes_1))
    plt.xticks([x for x in range(1,9)])
    #ax.set_title('Comparison of Admissible and Complete Semantics',fontsize="medium")
    plt.show()

#Tex Style writer, takes items from a list and places them
def tex_style_writer(args,printflag):
    dict_style = []
    for x in range(0,len(args[0])):
        dict_style.append("${}$ & ${}$ & ${}$ & ${}$ \\ ".format(args[1][x],args[2][x],args[3][x]))
    if printflag == 1:
        for line in dict_style:
            print(dict_style)
    else: return dict_style

#tex_style_writer([range(1,13),np.round(class_time,4),np.round(tri_time,4),speed_factor],1)

#Tex Style writer for multiple interpretations
def tablecontent_creator():
    semantics = [["a"],["c"]]
    # create head
    table_head = ["Nodes"]
    for singSem in semantics:
        table_head += ["{}".format(singSem), "tri-{}".format(singSem), "Speed"]
    final_table = [table_head]

    # create body
    for nodenbr in range(1,9):
        table_row = [nodenbr]
        for singSem in semantics:
            nbr,two,tri = get_results(nodenbr,singSem)
            speed = np.divide(two,tri)
            [table_row.append(x) for x in [two,tri,speed]]
        final_table.append(table_row)
    return final_table
tablecontent_creator()

def mult_tex_writer(dataTable):
    lendatastream = len(dataTable[0])
    templaterowTemp = r"{}\\"
    dataheadraw = "{}&" * lendatastream
    dataheadraw = dataheadraw[:-1]
    datahead = dataheadraw.format(*dataTable[0])
    print("c|" * len(dataTable[0]))
    print(templaterowTemp.format(datahead))
    for dataRow in dataTable[1:]:
        dataRowRaw = "${}$&" * lendatastream
        dataRowRaw = dataRowRaw[:-1]
        rounded = [np.round(x, 4) for x in dataRow[:-1]]
        rounded.append(np.round(dataRow[-1], 2))
        formated = dataRowRaw.format(*rounded)
        print(templaterowTemp.format(formated))

def mult_html_writer(dataTable):
    lendatastream = len(dataTable[0])
    templaterowTemp = r"<tr>{}$</tr>"
    dataheadraw = "<th>{}</th>" * lendatastream
    datahead = dataheadraw.format(*dataTable[0])
    print(templaterowTemp.format(datahead))
    for dataRow in dataTable[1:]:
        dataRowRaw = "<td>{}</td>" * lendatastream
        rounded = [np.round(x, 4) for x in dataRow[:-1]]
        rounded.append(np.round(dataRow[-1], 2))
        formated = dataRowRaw.format(*rounded)
        print(templaterowTemp.format(formated))

#mult_tex_writer(tablecontent_creator())
#mult_html_writer(tablecontent_creator())

mult_tex_writer(tablecontent_creator())
plot_gain(1,8,["a"],["c"],"adm","cmp")


