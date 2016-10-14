# author : g1n0st
import requests, sys, re, io, os
#options
_ONLY_ACCEPTED_ = False
_DELETE_HEAD_NOTE_ = False
_SET_PATH_ = False
_PATH_ = ''
#const web url
login_url = 'http://www.lydsy.com/JudgeOnline/login.php'
userinfo_url = 'http://www.lydsy.com/JudgeOnline/userinfo.php?user='
code_url = 'http://www.lydsy.com/JudgeOnline/status.php?problem_id='
showcode_url = 'http://www.lydsy.com/JudgeOnline/'

# {name, password}
username = ''
password = ''

#session bin
s = requests.Session()

# appear times
all_state = ['Compile_Error',
             'Accepted',
             'Wrong_Answer',
             'Runtime_Error',
             'Time_Limit_Exceed',
             'Presentation_Error',
             'Memory_Limit_Exceed',
             'Output_Limit_Exceed']
pool = {
            'Compile_Error' : 0,
            'Accepted' : 0,
            'Wrong_Answer' : 0,
            'Runtime_Error' : 0,
            'Time_Limit_Exceed' : 0,
            'Presentation_Error' : 0,
            'Memory_Limit_Exceed' : 0,
            'Output_Limit_Exceed' : 0
}
nown = ''

postfix = {
            'C++' : '.cpp',
            'C' : '.c',
            'Pascal' : '.pas',
            'Python' : '.py'
}
def Value(prefix, op) :
    i = prefix.find(op)
    clen = len(prefix)
    ret = ''
    while (i < clen) :
        i += 1
        if (prefix[i - 1] == ' ') : break
    while (i < clen) :
        ret += prefix[i]
        i += 1
        if (prefix[i] == ' ' or prefix[i] == '\n') : break
    return ret

def Delsc(code) :
    code = code.replace('&lt;', '<')
    code = code.replace('&gt;', '>')
    code = code.replace('&quot;', '\"')
    code = code.replace('&amp;', '&')
    code = code.replace('&nbsp', ' ')
    code = code.replace('\n', '')
    return code
def Getcode(ID, key, path) :
    global nown;

    page = s.get(showcode_url + key)
    code = re.search('(\<pre)(.|\n)*(?=\</pre\>)', page.text).group()

    i = 0
    clen = len(code)
    while (i < clen) :
        i += 1
        if (code[i - 1] == '>') : break
    code = code[i : clen]
    #print(code) input()

    j = i
    while (j < clen) :
        j += 1
        if (code[j - 1] == '/') : break
    prefix = code[0 : j]

    if not _ONLY_ACCEPTED_ :
        state = Value(prefix, 'Result')
        filename = state + '_' + str(pool[state]) + postfix[Value(prefix, 'Language')]
        pool[state] += 1
    else :
        filename = ID + postfix[Value(prefix, 'Language')]

    fp = open(path + '\\' + filename, 'w', encoding = 'utf-8')
    if (not _DELETE_HEAD_NOTE_) :
        fp.write(code[0 : j] + '\n')
    fp.write(Delsc(code[j + 1 : clen]))

def Download(ID) :
    global pool, nown

    cur_url = code_url + ID + '&user_id=' + username
    if (_ONLY_ACCEPTED_) : cur_url += '&jresult=4'
    page = s.get(cur_url)
    links = re.findall('showsource.php\?id=[0-9]+', page.text)

    if (ID != nown) :
        for key in all_state :
            pool[key] = 0
            nown = ID
    n_path = _PATH_ + ('\\' + ID)
    if (os.path.exists(n_path) == False) : os.mkdir(n_path)

    for i in links :
        Getcode(ID, i, n_path)
        if (_ONLY_ACCEPTED_) : break

def Login() :
    #set console output string format 'utf8'
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding = 'utf8')

    ret = s.post(login_url, {'user_id': username, 'password': password}).text
    if (ret.find('-2') == -1) :
        print('Password or username is incorrect.')
        sys.exit()
    r = s.get(userinfo_url + username)

    passed = re.findall('p\([0-9]+\)', r.text)
    print('The problems in BZOJ you\'ve passed :\n', passed)

    for i in passed :
        Download(i[2 : 6])
def Help() :
    print ('Usage:\n  python bzojcc.py [options]')
    print ('\nOptions:')
    print (' --help, -h                      Show help.')
    print (' --name, -n <user_id>            Bzoj username (*).')
    print (' --password -p <password>        Bzoj password (*).')
    print (' --save -s <path>                Path to save code (Default current directory).')
    print (' --unnote -u                     Delete note ahead of codes.')
    print (' --accepted -a                   Only save \'Accepted\' state codes.')

def Argv(argv) :
    global username, password
    global _PATH_, _SET_PATH_, _DELETE_HEAD_NOTE_, _ONLY_ACCEPTED_
    i = 1
    while (i < len(argv)) :
        if argv[i] == '--name' or argv[i] == '-n' :
            if (i + 1 >= len(argv)) : sys.exit()
            username = argv[i + 1]
            i += 1
        elif argv[i] == '--password' or argv[i] == '-p' :
            if (i + 1 >= len(argv)) : sys.exit()
            password = argv[i + 1]
            i += 1
        elif argv[i] == '--save' or argv[i] == '-s' :
            if (i + 1 >= len(argv)) : sys.exit()
            _PATH_ = argv[i + 1]
            _SET_PATH_ = True
            i += 1
        elif argv[i] == '--unnote' or argv[i] == '-u' :
            _DELETE_HEAD_NOTE_ = True
        elif argv[i] == '--accepted' or argv[i] == '-a' :
            _ONLY_ACCEPTED_ = True
        else :
            print ("Undefined option: " + argv[i])
            sys.exit()
        i += 1

    if (username == '') :
        print ('Username is not input.')
        sys.exit()
    if (password == '') :
        print ('Password is not input.')
        sys.exit()
    if (_SET_PATH_ == False) : _PATH_ = os.getcwd()
    _PATH_ += '\\' + username
    if (os.path.exists(_PATH_) == False) : os.mkdir(_PATH_)

if __name__ == "__main__" :
    if len(sys.argv) == 1 or sys.argv[1] == '--help' or sys.argv[1] == '-h' :
        Help()
    else :
        Argv(sys.argv)
        Login()
