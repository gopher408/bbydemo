import os

class BanterConfig:
    def __init__(self, partner, grammar_file, dictionary_file = None):
        currentLocation = os.path.dirname(os.path.abspath(__file__))
        self.curr_path = os.path.join(currentLocation, '..')
        self.partner = partner
	self.common = 'common'
	self.com_path = ''
	self.partner_path = ''
        self.grammar_file = grammar_file
        self.global_dict = ''
        self.local_dict = ''
        self.set_com_path()
        self.set_partner_path()

    def get_common(self):
        return self.common

    def set_com_path(self):
	comPath = os.path.join(self.curr_path, self.common)
        if os.path.isdir(comPath):
           self.com_path = os.path.join(self.curr_path, self.common)
	else:
           self.com_path = self.curr_path

    def get_com_path(self):
#        print 'BanterConfig.get_com_path():' + self.com_path
        return self.com_path

    def get_dictionary_file(self, dictionary_file = None):
        if dictionary_file != None:
           self.global_dict = dictionary_file
	else:
           self.global_dict = 'dictionary.txt'
#        print 'BanterConfig.dictionary_file:' + os.path.join(self.get_com_path(), self.global_dict)
        return os.path.join(self.get_com_path(), self.global_dict)

    def get_partner(self):
        return self.partner

    def set_partner_path(self):
        if len(self.partner) > 0:
            tmpPath = os.path.join(self.curr_path, 'partner', self.partner)
            if os.path.isdir(tmpPath):
               self.partner_path = os.path.join(self.curr_path, 'partner', self.partner)
	    else:
               self.partner = ''
	       self.partner_path = self.curr_path

    def get_partner_path(self):
#        print 'BanterConfig.get_partner_path():' + self.partner_path
        return self.partner_path

    def get_grammar_file(self, grammar_file = None):
        if grammar_file != None:
           self.grammar_file = grammar_file
        if len(self.get_partner_path()) == 0:
           return os.path.join(self.get_com_path(), self.grammar_file)
	else:
           return os.path.join(self.get_partner_path(), self.grammar_file)

    def get_words_file(self, file_name = None):
	if file_name != None:
           self.local_dict = file_name
        else:
#           self.local_dict = os.path.join(self.get_com_path(), 'words.txt')
           self.local_dict = os.path.join(self.get_partner_path(), 'words.txt')
#        print 'BanterConfig.get_words_file:' + os.path.join(self.get_partner_path(), self.local_dict)
        return os.path.join(self.get_partner_path(), self.local_dict)

    def get_dict_terms(self):
        dict_terms = []
        with open(self.get_dictionary_file()) as f:
            lines = f.readlines()
            for line in lines:
        	if line[0] in ['#', '\t', '\n', '\r\n']:
           	   pass
        	else:
           	   if line[-2] == ' ':
              	      temp = line[:len(line)-2]
           	   else:
              	      temp = line[:len(line)-1]
                   dict_terms.append(temp)
        with open(self.get_words_file()) as f:
            lines = f.readlines()
            for line in lines:
               dict_terms.append(line.strip())
        dict_terms = list(set(dict_terms))
	return dict_terms
