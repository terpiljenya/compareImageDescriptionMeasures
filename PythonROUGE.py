"""
Created on Mon Aug 13 10:31:58 2012

author: Miguel B. Almeida
mail: mba@priberam.pt
"""

import os
import re
import sys

# Wrapper function to use ROUGE from Python easily
# Inputs:
    # guess_summ_list, a string with the absolute path to the file with your guess summary
    # ref_summ_list, a list of lists of paths to multiple reference summaries.
    # IMPORTANT: all the reference summaries must be in the same directory!
    # (optional) ngram_order, the order of the N-grams used to compute ROUGE
    # the default is 1 (unigrams)
# Output: a tuple of the form (recall,precision,F_measure)
#
# Example usage: PythonROUGE('/home/foo/my_guess_summary.txt',[/home/bar/my_ref_summary_1.txt,/home/bar/my_ref_summary_2.txt])
def PythonROUGE(guess_summ_list,ref_summ_list,ngram_order=4):
    """ Wrapper function to use ROUGE from Python easily. """

    # even though we ask that the first argument is a list,
    # if it is a single string we can handle it
    if type(guess_summ_list) == str:
        temp = list()
        temp.append(ref_summ_list)
        guess_summ_list = temp
        del temp
    
    # even though we ask that the second argument is a list of lists,
    # if it is a single string we can handle it
#    if type(ref_summ_list[0]) == str:
#        temp = list()
#        temp.append(ref_summ_list)
#        ref_summ_list = temp
#        del temp
    
    # this is the path to your ROUGE distribution
    ROUGE_path = 'RELEASE-1.5.5/ROUGE-1.5.5.pl'
    data_path = 'RELEASE-1.5.5/data'
    
    # these are the options used to call ROUGE
    # feel free to edit this is you want to call ROUGE with different options
    options = "-a -m -n 1 -u -2 4 -t 1 -f B" # -f A -> average  // -f B -> best
    # this is a temporary XML file which will contain information
    # in the format ROUGE uses
    xml_path = 'temp.xml'
    xml_file = open(xml_path,'w')
    xml_file.write('<ROUGE-EVAL version="1.0">\n')
    for guess_summ_index,guess_summ_file in enumerate(guess_summ_list):
        xml_file.write('<EVAL ID="' + str(guess_summ_index+1) + '">\n')
        create_xml(xml_file,guess_summ_file,ref_summ_list[guess_summ_index])
        xml_file.write('</EVAL>\n')
    xml_file.write('</ROUGE-EVAL>\n')
    xml_file.close()

    appender = guess_summ_list[0].split("/")[-1]
    #appender = 0
    
    # this is the file where the output of ROUGE will be stored
    ROUGE_output_path = 'ROUGE_result/'+str(appender)
    
    # this is where we run ROUGE itself
    exec_command = ROUGE_path + ' -e ' + data_path + ' ' + options + " " +  xml_path + ' > ' + ROUGE_output_path
    os.system(exec_command)

    # here, we read the file with the ROUGE output and
    # look for the recall, precision, and F-measure scores
    recall_list = list()
    precision_list = list()
    F_measure_list = list()
    ROUGE_output_file = open(ROUGE_output_path,'r')
    for n in xrange(ngram_order):
        ROUGE_output_file.seek(0)
        for line in ROUGE_output_file:
            match = re.findall('X ROUGE-' + str(n+1) + ' Average_R: ([0-9.]+)',line)
            if match != []:
                recall_list.append(float(match[0]))
            match = re.findall('X ROUGE-' + str(n+1) + ' Average_P: ([0-9.]+)',line)
            if match != []:
                precision_list.append(float(match[0]))
            match = re.findall('X ROUGE-' + str(n+1) + ' Average_F: ([0-9.]+)',line)
            if match != []:
                F_measure_list.append(float(match[0]))
    ROUGE_output_file.close()
    
    # remove temporary files which were created
    os.remove(xml_path)
    #os.remove(ROUGE_output_path)

    return (recall_list,precision_list,F_measure_list)
    
    
# This is an auxiliary function
# It creates an XML file which ROUGE can read
# Don't ask me how ROUGE works, because I don't know!
def create_xml(xml_file,guess_summ_file,ref_summ_list):
    xml_file.write('<PEER-ROOT>\n')
    guess_summ_dir = os.path.dirname(guess_summ_file)
    xml_file.write(guess_summ_dir + '\n')
    xml_file.write('</PEER-ROOT>\n')
    xml_file.write('<MODEL-ROOT>\n')
    ref_summ_dir = os.path.dirname(ref_summ_list[0] + '\n')
    xml_file.write(ref_summ_dir + '\n')
    xml_file.write('</MODEL-ROOT>\n')
    xml_file.write('<INPUT-FORMAT TYPE="SPL">\n')
    xml_file.write('</INPUT-FORMAT>\n')
    xml_file.write('<PEERS>\n')
    guess_summ_basename = os.path.basename(guess_summ_file)
    xml_file.write('<P ID="X">' + guess_summ_basename + '</P>\n')
    xml_file.write('</PEERS>\n')
    xml_file.write('<MODELS>')
    letter_list = ['A','B','C','D','E','F','G','H','I','J']
    for ref_summ_index,ref_summ_file in enumerate(ref_summ_list):
        ref_summ_basename = os.path.basename(ref_summ_file)
        xml_file.write('<M ID="' + letter_list[ref_summ_index] + '">' + ref_summ_basename + '</M>\n')
    
    xml_file.write('</MODELS>\n')

if __name__ == "__main__":
  hyp_file = sys.argv[1]
  ref_file = sys.argv[2:]
  
  print
  print "H:" + hyp_file
  print "R:" + str(ref_file)

  hyp_file_list = [hyp_file]
  ref_file_list = [ref_file]
  recall_list,precision_list,F_measure_list = PythonROUGE(hyp_file_list,ref_file_list)
  print 'recall = ' + str(recall_list)
  print 'precision = ' + str(precision_list)
  print 'F = ' + str(F_measure_list)