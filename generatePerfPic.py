import os
import exceptions
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser
from decimal import Decimal


def main():
    parser = OptionParser()
    parser.add_option("-c", "--CurrentResult", dest="current_result", help="CurrentResult")
    parser.add_option("-b", "--BaselineResult", dest="baseline_result", help="BaselineResult")
    parser.add_option("-d", "--BuildNumber", dest="buildNumber", help="BuildNumber", default="CurrentBuild")
    parser.add_option("-o", "--OutPut", dest="output", help="OutPut", default=".")
    (options, args) = parser.parse_args()
    
    resultDic = {}
    # scrum team ask for this step order, so hardcode here. if there is new step add in test case or name changed, need to upate here.
    orderedList = ["UploadProject","UploadProject_WholeProcess","OpenCollaborationProject","Checkindwg(6MB)","Checkoutdwg(6MB)","RefreshProject"]
    
    def GetDataFromFile(fileName):
        tempDic = {}
        with open(fileName) as f:              
            for x in f.readlines():
                if len(x.strip('\n'))!=0:
                    temp = x.replace(" ", "").strip('\n').split(':')
                    tempDic[temp[0]] = float(temp[1])
        return tempDic
    
    def GetValuesByExpectedOrder(handleDict):
        values=[] 
        for o in orderedList:
            if(handleDict.has_key(o)):
                values.append(handleDict[o])
            else:
                raise Exception('handleDict not contain key: {0}. please make sure orderedList items correct!'.format(o))
        return values
    
    def DrawTrendPic(resultDict, output):   
        keys=orderedList
        # get values by scrum tead asked order.
        values=GetValuesByExpectedOrder(resultDict)                    
        """
        # sort resultDict by key and append key, values to related list.
        for key in sorted(resultDict.iterkeys()):
            keys.append(key)
            values.append(resultDict[key])                  
        print "INFO: show values:  %s" % values
        """       
        fig, ax = plt.subplots()
        ax.set_axis_bgcolor('#F6F4EA')
        index = np.arange(len(values))
        bar_width = 0.3
        opacity = 0.4
        rects1 = plt.bar(index, tuple(values), bar_width,
                    alpha=opacity,
                    color='#4F81EF',
                    label='Response%')

        plt.title('Trends by step')
        plt.xticks(index - bar_width*0.5, tuple(keys), rotation=30, ha='left',fontsize=11)       
        #ax.set_yticks(np.arange(-30, 35, 5))

        for rect in rects1:
            height = rect.get_height()
            if rect.get_y() < 0:
                value = str(-height)
                ax.text(rect.get_x()+rect.get_width()/2, Decimal('-1.05')*height, value, ha='center', va='bottom', fontsize=12)
            else:
                value = str(height)
                ax.text(rect.get_x()+rect.get_width()/2, Decimal('1.05')*height, value, ha='center', va='bottom', fontsize=12)
        #plt.xlabel('Step')
        plt.legend(loc="upper right")
        plt.grid(True)
        fig=plt.gcf()
        fig.set_size_inches(13, 13)
        plt.savefig(output, dpi=100)
    
    
    def DrawComparePic(baselineResult, currentResult, buildNumber, output):
        tempDict = {}             
        # only baseline contained key will be show in compare png.
        for key in baselineResult:
            if(currentResult.has_key(key)):
                tempDict[key] = currentResult[key]                 
       
        keys=orderedList
        # get baseline values by scrum tead asked order.
        valuesBase=GetValuesByExpectedOrder(baselineResult)
        # get current values by scrum tead asked order.
        valuesCurrent=GetValuesByExpectedOrder(tempDict)       
        print "keys:"
        print keys
    
        fig, ax = plt.subplots()  
        index = np.arange(len(valuesBase))  
        bar_width = 0.35    
        opacity = 0.4  
        rects1 = plt.bar(index, valuesBase, bar_width,alpha=opacity, color='b',label='Baseline')  
        rects2 = plt.bar(index + bar_width, valuesCurrent, bar_width,alpha=opacity,color='r',label=buildNumber)        
        
        # show the response time at the top of every pillar
        for rect in rects1:
            ax.text(rect.get_x()+rect.get_width()/2, rect.get_height(), rect.get_height(), ha='center', va='bottom', fontsize=12)       
        for rect in rects2:
            ax.text(rect.get_x()+rect.get_width()/2, rect.get_height(), rect.get_height(), ha='center', va='bottom', fontsize=12)
                
        plt.xlabel('Step')  
        plt.ylabel('Response time(seconds)')  
        plt.title('Response time by build and step')     
        plt.xticks(index - bar_width*0.45, tuple(keys), rotation=31, ha='left', fontsize=11)      
        plt.legend(loc="upper right")   
        fig=plt.gcf()
        fig.set_size_inches(13, 13)
        plt.savefig(output, dpi=100)   
      
    
    # get data from baseline and current result txt file
    currentDic = GetDataFromFile(options.current_result)   
    baseDic = GetDataFromFile(options.baseline_result)
    print "INFO: currentDic: %s" % currentDic
    print "INFO: baseDic: %s" % baseDic
    
    for key in currentDic:
        if(baseDic.has_key(key)):
            resultDic[key]=Decimal('%.2f' % float((currentDic[key]-baseDic[key])/baseDic[key]*100))
        else:
            print 'WARNING: baseline not contain item:['+key+']! Ignore it on perf report!!!'              
    print "INFO: resultDic: %s" % resultDic      
     
    DrawTrendPic(resultDic, os.path.join(options.output, "plantPerfResult.png"))
    DrawComparePic(baseDic, currentDic, options.buildNumber, os.path.join(options.output, "plantCompareResult.png"))

    
if __name__ == "__main__":
    main()
