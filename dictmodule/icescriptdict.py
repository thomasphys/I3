class icetraydict :

  def __init__(self,infile):
    if os.path.isfile(infile):
      #load from file                                                           
      f = open(infile,"r")                                                      
      filelines = f.readlines()

      current_dict_name = ''
      indict = False
      dict_temp = {"temp":"temp"}

      for line in filelines :                                                   
        key_value = str.split(line)
        if indict :
          if key_value[0] == '}'
            indict = False
            self.icedict[current_dict_name] = dict_temp
          elif key_value[1] == 'int':                                             
            dict_temp[key_value[0]] = int(key_value[2])                        
          elif key_value[1] == 'float' :                                          
            dict_temp[key_value[0]] = float(key_value[2])                      
          elif key_value[1] == 'str' :                                            
            dict_temp[key_value[0]] = key_value[2] 
        elif key_value[1] == 'int':
          self.icedict[key_value[0]] = int(key_value[2])
        elif key_value[1] == 'float' :
          self.icedict[key_value[0]] = float(key_value[2])
        elif key_value[1] == 'str' :
          self.icedict[key_value[0]] = key_value[2]
        elif key_value[1] == 'dict':
          current_dict_name = key_value[0]
          dict_temp = {"name":key_value[2]}
          indict = True
      self.icedict["parentfile"] = self.icedict["name"]

    else :
      self.icedict = {"name":infile} 

  def PrinttoFile(self,outfile):
    self.icedict["name"] = outfile
    f = open(outfile,"w+")
    for key in self.icedict.keys() :
      if(type(self.icedict[key]) == 'dict'
        f.write("%s %s %s" % key,type(self.icedict[key]),self.icedict[key]) 
        f.write("{")
        for subkey in self.icedict[key].keys() :
          f.write("%s %s %s" % subkey,type(self.icedict[key][subkey]),self.icedict[key][subkey])
        f.write("}")
      else :
        f.write("%s %s %s" % key,type(self.icedict[key]),self.icedict[key])
    f.close()

  def Get(self,key,subkey):
    #returns integer
    if subkey = "":
      return self.icedict[key]
    else return self.icedict[key][subkey]

  def Add(self,key,value) :
    if type(value) == 'int':
      self.icedict[key] = str("%d" % value)
    elif type(value) == 'float':
      self.icedict[key] = str("%f" % value) 
    elif type(value) == 'str':
      self.icedict[key] = value
    elif type(value) == 'dict':
      self.icedict[key] = value
    return value

  def AddSub(self,key,subkey,value) :
    if type(value) == 'int':                                                     
      self.icedict[key][subkey] = str("%d" % value)                                     
    elif type(value) == 'float':                                                 
      self.icedict[key][subkey] = str("%f" % value)                                     
    elif type(value) == 'str':                                                   
      self.icedict[key][subkey] = value
    elif type(value) == 'dict' :
      print("Error: can not add sub sub dictionary")
    return value


