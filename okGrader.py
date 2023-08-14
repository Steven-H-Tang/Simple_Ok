import importlib
import pickle
import os
import doctest

#This file is only part that needs to be rewritte for every other proj.
#provides a way to map the question number to its locked function.
#test_map is from this file
from test_map_file import *
def test_to_func(s):
    return test_map.get(s)


test_folder="tests"

#Some suites are dozens of questions long, this limits the max case number
question_limit = 3




'''
Clears the history to its original empty state, also writes an empty save file when
it doesn't exist.
Iterate through every file in the "test" folder, and saves whether it has been answered
or not, along with whether its related doctest is passed.
A two-index array, save[0] is an array of whether each unlock-question has been passed,
and save[1] is a bool of whether the doc test has been passed.
'''
def clear_history():
    
    test_files = [f for f in os.listdir(test_folder) if f.endswith('.py') and f[:2].isdigit()]
    save ={}
    for t in test_files:
        save_name = t[:-3] 
        save_file = importlib.import_module(f"{test_folder}.{save_name}")
        
        save[save_name]=[[],False]
        limit=0
        for _ in save_file.test["suites"][0]["cases"]:
            save[save_name][0].append(False)
            limit+=1
            if limit == question_limit:
                break
            

    return write(save,"save")


'''
Writed down the "save" down into a file
'''
def write(content, file):
    with open(f'{file}.pkl', 'wb') as f:
        pickle.dump(content, f)
    return content


'''
Displays whether each unlock-question is passed, and if its doctest is
locked, not passed, or passed.
'''
def show_scores(save):

    for t in save:
        unlocked = True
        for i in save[t][0]:
            if not i:
                unlocked = False
        if unlocked:
             print(f'{t} unlocked: {unlocked};    doctest: {save[t][1]}')
        else:
             print(f'{t} unlocked: {unlocked};    doctest: locked')
        



'''
read a string into an array of lines
'''
def read_lines(code):
    result=[""]
    index=0
    had_new_line = True
    for i in range(len(code)):
        c=code[i]
        if not c.isspace():
            result[index]+=c
            had_new_line = False
        elif c=="\n":
            if not had_new_line:
                result.append("")
                index+=1
                had_new_line=True
        else:
            if not had_new_line:
                 result[index]+=c
    return result[:-1]


'''
This goes into the file with pre-writtens tests, and break them into arries.
If a line starts with >>>, we print the line.
Other wise, we wait for the user to input repeatedly until the correct input is received
Then, we update the save and writes it down.
Supports "code" type of question, not "choice" type for now.
Inputing a single q at this stage will quit out if it's not the answer
'''
def ok_unlock(save, q_num):
    unlock_test_file = importlib.import_module(f"{test_folder}.{q_num}")
    questions=unlock_test_file.test["suites"][0]["cases"]
    question_num=(min(question_limit,(len(questions))))
    for i in range (question_num):
        if save[q_num][0][i]:
            continue

        code=questions[i].get("code")
        code=read_lines(code)
        print(f'Case {i+1} out of {question_num}')
        for line in code:
            if line[:3]==">>>":
                print(line)
            else:
                correct = False
                answer = input("").strip()
                while not correct:
                    if (answer=="q" or answer =="Q") and answer!=line:
                        save = write(save,"save")
                        return save
                    if answer==line:
                        correct=True
                    else:
                        answer = input("Wrong Answer! Try again\n").strip()
                    
        save[q_num][0][i]=True

    save = write(save,"save")
    print(f'\nAll questions for q {q_num} unlocked!\n')
    return save


'''
If the test is unlocked, attempts doctest on it, and updates the save according.
'''
def ok_doctest(save, q_num):
    for i in save[q_num][0]:
            if not i:
                print("Test not unlocked yet!")
                return

    if check_output(doctest.run_docstring_examples,(test_to_func(q_num),globals()),""):
        save[q_num][1]=True
        save = write(save,"save")
        print(f'\nAll doctest for q {q_num} passed!\n')
    else:
        save[q_num][1]=False
        save = write(save,"save")
        print(f'\nDoctest Failed!\n')

    return save



#This is a random function found online to check whether a function has any 
#printed statements.
#This is used to detect whether a doctext passed
import sys
import io
def check_output(func, args, expected_printed=None):
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    func(*args)
    sys.stdout = old_stdout
    printed_output = new_stdout.getvalue().strip() 
    print(printed_output)
    return printed_output == expected_printed



def main():
    # Loads the save
    try:
        with open('save.pkl', 'rb') as f:
            save = pickle.load(f)
    except FileNotFoundError:
        save=clear_history()


    # Parse Commands
    while True:
        command = input("Enter your command (or 'ok quit' to quit): ").strip()
        parts = command.split()

        

        if len(parts) < 2 or len(parts) > 4 or parts[:1] != ["ok"]:
            print("Invalid command. Expected format: ok -q <action>")
            continue
        
        '''
        Supports the 3 commands:
        ok clear
            -- resets the history to its original state for testing purpose
        ok quit
            -- quits the program
        ok score
            -- shows progress so far
        '''
        if len(parts)==2:
            action = parts[1]
            if action=="clear":
                print("\nHistory Cleared! \n")
                save=clear_history()
            elif action=="quit":
                break
            elif action=="score":
                show_scores(save)
            else:
                print("Invalid command: Invalid Action Len 2")


        '''
        Supports the commands:
        ok -q <question number>
        '''
        if len(parts)==3:
            action = parts[2]
            if action.isdigit and save.get(action):
                ok_doctest(save,action)
            else:
                print("Invalid command: Invalid Action Len 3")


        '''
        Supports the commands:
        ok -q <question number> -u
        '''
        if len(parts)==4:
            action, flag = parts[2],parts[3]
            if action.isdigit and flag =="-u" and save.get(action):
                save=ok_unlock(save,action)
            else:
                print("Invalid command: Invalid Action Len 4")
                
        
        
        

if __name__ == "__main__":
    main()