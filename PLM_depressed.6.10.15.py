
# coding: utf-8

# In[77]:

import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import os
import re
import pandas as pd
import time
import random
import json


# In[2]:

chromedriver = '/Users/tjyacoub/Downloads/chromedriver'
os.environ["webdriver.chrome.driver"] = chromedriver


# In[3]:

driver = webdriver.Chrome(chromedriver)


# In[4]:

driver.get('http://www.patientslikeme.com/login')


# In[462]:

xpaths = {'login':'//*[@id="userlogin_login"]', 'password':'//*[@id="userlogin_password"]', 'submit':'//*[@id="frm-login-only"]/div/input'}
username = 'testpatient1986'
password = 'patientspassword'


# In[4]:

monthDict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}


# In[10]:

def click(xpath):
    driver.find_element_by_xpath(xpath).click()
    
def send(xpath, string):
    driver.find_element_by_xpath(xpath).send_keys(string)
    
def get_text(xpath):
    return driver.find_element_by_xpath(xpath).text

def sleep():
    seconds = 4 + random.random() * 3
    time.sleep(seconds)
    
def ifint(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


# In[411]:

sleep()


# In[463]:

driver.find_element_by_xpath(xpaths['login']).clear()
#Write Username in Username TextBox
driver.find_element_by_xpath(xpaths['login']).send_keys(username)
#Clear Password TextBox if already allowed "Remember Me" 
driver.find_element_by_xpath(xpaths['password']).clear()

#Write Password in password TextBox
driver.find_element_by_xpath(xpaths['password']).send_keys(password)

#Click Login button
driver.find_element_by_xpath(xpaths['submit']).click()


# In[6]:

driver.get('https://www.patientslikeme.com/symptoms')


# In[6]:

# Go to 'Depressed Mood' symptom
driver.get('https://www.patientslikeme.com/symptoms/show/3-depressed-mood')


# In[8]:

# Click filter menu
click('//*[@id="condition-filter"]/div/a')

# Remove bipolar filter
click('//*[@id="condition-filter-menu"]/li[1]/a')

# Go to 'depressed mood'
click('//*[@id="pg-index"]/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div[3]/div[1]/h3/a')


# In[5]:

# Get last login from patient summary page
def get_id():
    url = driver.current_url
    #print url
    numbers = re.findall(r'(\d+)', str(url))
    return int(numbers[0])
    
def get_login():
    id_num = get_id()
    #path = '//*[@id="other-conditions-' + str(id_num) + '"]/div/div[1]/div[3]'
    path = '//div[@class="helptext"]'
    text = driver.find_element_by_xpath(path).text
    #print text
    last_login_month = monthDict[str(text[38:41])]
    last_login_year = int(text[46:51])
    return last_login_month, last_login_year


# In[69]:

# Go through drugs

def cycle_drugs():
    
    
    num_drugs = 5
    num_data_points = 0
    for i in range(1, num_drugs+1):
        driver.get('https://www.patientslikeme.com/symptoms/show/3-depressed-mood?page=1')
        sleep()
        # Get drug name
        drug_name_path = '//*[@id="pg-show"]/div[3]/div[2]/div[2]/div[2]/div[1]/div[4]/table/tbody/tr[' + str(i) + ']/th/span/a'
        drug_name = get_text(drug_name_path)
        print drug_name
        if drug_name in generic_to_brand_Dict:
            drug_name = generic_to_brand_Dict[drug_name]
        
        # Go to patients taking drug 'i'
        patients_list_path = '//*[@id="pg-show"]/div[3]/div[2]/div[2]/div[2]/div[1]/div[4]/table/tbody/tr[' + str(i) + ']/td[1]/a'
        click(patients_list_path)
        sleep()
        
        # Get number of patients taking drug 'i'
        num_patients_path = '//*[@id="pg-treatment"]/div[3]/div[2]/div/div[2]/p/b'
        num_patients_text = get_text(num_patients_path)
        num_patients = int(num_patients_text.split()[-1].replace(',',''))
        #print num_patients
        
        # Number of pages with patients taking drug 'i'
        patients_per_page = int(num_patients_text.split()[2])
        num_pages = int(num_patients/patients_per_page) 
        if num_patients%patients_per_page != 0: 
            num_pages += 1
        
        ## FOR TESTING
        num_pages = 3
        patients_per_page = 2
        
        for page_rank in range(num_pages):
            
            for patient_rank in range(1, patients_per_page + 1):
                
                # Get patient name
                patient_name_path = '//*[@id="pg-treatment"]/div[3]/div[2]/div/div[3]/div/div[2]/div[' + str(patient_rank) + ']/div[1]/div[2]/div[3]/div/a'
                #print patient_name_path
                #patient_name = get_text(patient_name_path)
                #print patient_name
                
                # Get id
                wait(patient_name_path)
                try:
                    link = driver.find_element_by_xpath(patient_name_path)
                    url = link.get_attribute("href")
                    nums = re.findall(r'(\d+)', str(url))
                    patient_id = int(nums[0])
                    print "patient_id", patient_id
                
                    click(patient_name_path)
                    sleep()
                
                    if patient_id not in data:
                        print "NEW PATIENT id", patient_id
                    
                        data[patient_id] = {}
                        data[patient_id][drug_name] = {}
                        print "data", data
                        try:
                            get_patient_info(patient_id, drug_name)
                        except:
                            "Error: Did not get patient info (1)"
                        
                    elif drug_name not in data[patient_id]:
                        print "NEW DRUG patient", patient_id, "drug", drug_name
                        print "data", data
                        data[patient_id][drug_name] = {}
                    
                        try:
                            get_patient_info(patient_id, drug_name)
                        except:
                            "Error: Did not get patient info (2)"
                    
                    #driver.back()
                    #else:
                        #print data
                        #print "patient", patient_name, "already has a profile for ", drug_name
                        # Back to patients list
                        #driver.back()
            
                # Go back to patients list page
                    driver.back()
                    sleep()
                    num_data_points += 1
                    if num_data_points % 100 == 0:
                        with open('PLM_depressed_data.json','w') as out:
                        json.dump(data, out)
                except:
                    print "Error: unable to get patient info"
                
            # Go to next page
            try:
                next_path = '//*[@id="pg-treatment"]/div[3]/div[2]/div/div[2]/div[2]/div[2]/div/a[5]/span'
                wait(next_path)
                click(next_path)
                sleep()
            except:
                print "Error: could not go to next set of patients"


# In[46]:

next_path = '//*[@id="pg-treatment"]/div[3]/div[2]/div/div[2]/div[2]/div[2]/div/a[5]/span'
wait(next_path)
click(next_path)


# In[47]:

def wait(xpath):
    delay = 20
    try:
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,xpath)))
        
    except TimeoutException:
        print "took too much time"


# In[48]:

generic_to_brand_Dict = {'Sertraline':'Zoloft',
                        'Duloxetine':'Cymbalta',
                        'Escitalopram':'Lexapro',
                        'Citalopram':'Celexa',
                        'Fluoxetine':'Prozac',
                        'Venlafaxine':'Effexor',
                        'Bupropion':'Wellbutrin',
                        'Paroxetine':'Paxil',
                        'Aripiprazole':'Abilify',
                        'Mirtazapine':'Remeron',
                        'Desvenlafaxine':'Pristiq',
                        'Trazadone':'Oleptro',
                        'Nortriptyline':'Pamelor',
                        'Lamotrigine':'Lamictal',
                        'Milnacipran':'Savella',
                        'Pregabalin':'Lyrica',
                        'Amitriptyline':'Elavil',
                        'Buspirone':'Buspar',
                        'Imipramine': 'Tofranil',
                        'Budeprion':'Wellbutrin'}
            
brand_to_generic_Dict = {v: k for k, v in generic_to_brand_Dict.items()}
#drug_Dict = generic_to_brand_Dict
#drug_Dict.update(brand_to_generic_Dict)


# In[65]:

def get_patient_info(patient_id, drug_name):
    print "In patient info function"
    # Select all treatments
    
    # Get more info on patient summary
    xpath = '//*[contains(text(), "See more")]' 
    click(xpath)
    sleep()
    #click('//*[@id="content-body"]/div[1]/a')
    
    # Extract login details
    try:
        path = '//div[@class="helptext"]'
        text = driver.find_element_by_xpath(path).text
        last_login_month = monthDict[str(text[38:41])]
        last_login_year = int(text[46:51])
        print last_login_month, last_login_year, "last month, last year"
    except:
        print "Error: couldn't get login info"
        
    #Click on treatments menu
    try:
        xpath = '//*[@id="treatments"]/td/div/span[2]'
        wait(xpath)
        click('//*[@id="treatments"]/td/div/a')
        sleep()
    except:
        print "Error: could not click on treatments menu"
    
    
    try:
        elem_list = driver.find_elements_by_xpath('//*[@id="tx-chart-popup"]/li')
        num_symptoms = len(elem_list)
        print "num symptoms", num_symptoms
    except:
        print "Error: could not get number of symptoms"
        
    try:
        xpath = '//*[@id="tx-chart-popup"]/li[' + str(num_symptoms) + ']/a'
        wait(xpath)
        click(xpath)  
        sleep()
        print "Success, 'All Symptoms' clicked"
    except:
        print "Error: could not click on All Symptoms"
    # Go to patient history of drug
    
    #xpath = '//*[contains(text(), "' + drug_name + '")]'
    
    
    try:
        xpath = '//*[contains(text(), "' + drug_name + '")]'
        #go_to_drug_history(xpath, 'Sertraline')
        click(xpath)
        sleep()
        print "Success: Gone to drug page (Brand name found)"
    except:
        print "Drug", drug_name, "not found, trying generic"
        try:
            temp_drug_name = brand_to_generic_Dict[drug_name]
            xpath = '//*[contains(text(), "' + temp_drug_name + '")]'
            click(xpath)
            sleep()
            #go_to_drug_history(xpath, 'Zoloft')
            print "Success: Generic drug", temp_drug_name, "found"
        except:
            print "Error: Drug page not found"
    
    #wait(xpath)
    #click(xpath)
    
    # Get duration, final dose of treatment
    try:
        total_duration, final_dose = get_duration_dose(last_login_month, last_login_year)
    except:
        print "Error: could not get duration and dose"
        
    # Get drug evaluation data
    try:
        efficacy, side_effects, adherence = get_review()
    except:
        print "Error: could not get efficacy"
    # Store data

    #data[patient_id][drug_name] = {}
    #print data
    try:
        data[patient_id][drug_name]['total_duration'] = total_duration
        data[patient_id][drug_name]['final_dose'] = final_dose
        data[patient_id][drug_name]['efficacy'] = efficacy
        data[patient_id][drug_name]['side_effects'] = side_effects
        data[patient_id][drug_name]['adherence'] = adherence
    except:
        print "Error: could not update data"
        
    print data
    
    # Go back to patient summary
    driver.back()
    sleep()


# In[50]:

def get_review():
    try: 
        rating_text = driver.find_element_by_xpath('//*[@id="evaluation-group"]/div/div[1]/div/div[1]/ul').text
        side_effects = re.search("Effects: (\w+)", rating_text).group(1)
        ## Efficacy for depressed mood only!!!
        efficacy = re.search("mood: (\w+)", rating_text).group(1)
        adherence = re.search("Adherence: (\w+)", rating_text).group(1)
    except:
        efficacy = 'NaN'
        side_effects = 'NaN'
        adherence = 'NaN'
    return efficacy, side_effects, adherence


# In[64]:

def get_duration_dose(last_login_month, last_login_year):
    
    # Get dosage informations
    sleep()
    text = driver.find_element_by_id('dosage').text
    durations = text.split('\n')
    total_duration = 0
    #print durations
    for duration in durations:
        dur_split = duration.split()
        
        # Get daily dose
        dose_num = float(dur_split[0])
        measure = str(dur_split[1])
        if measure.lower == 'tablet':
            dose_num = 'NaN'
        if "twice" in dur_split: dose_num = dose_num * 2
        if "three" in dur_split: dose_num = dose_num * 3
        if "four" in dur_split: dose_num = dose_num * 4
            
        for c in range(len(dur_split)):
            if dur_split[c] in monthDict:
                year1 = 0
                year2 = 0
                month1 = monthDict[dur_split[c]]
                
                # if span is less than a month, c+3 will be an integer
                
                #[u'20', u'mg', u'Daily', u'Jul', u'01', u'-', u'01,', u'2003']
                print dur_split, dur_split[c]
                
                month_plus_three = dur_split[c+3]
                #try:
                #    x = dur_split[c+3]
                #    y = x[0]
                #except:
                #    x = dur_split[c+3]
                
                if ifint(month_plus_three[0]):
                    print "it's an int, span is less than one month"
                    month2 = month1
                    c = len(dur_split)
                   
                    
                # if year < span < month, c+3 will be another month
                elif month_plus_three in monthDict:
                    print "span is between a month and a year"
                    month2 = monthDict[month_plus_three]
                    c = len(dur_split)
                   # print dur_split, month1, month2, year1, year2#
                    
                # if  spans current, c+4 will be Last
                elif dur_split[c+4] == 'Last':
                    print "span is current"
                    year1 = int(dur_split[c+2])
                    month2 = last_login_month
                    year2 = last_login_year
                    c = len(dur_split)
                   # print dur_split, month1, month2, year1, year2
                    
                # if  span > year but not current 
                elif dur_split[c+4] != 'Last':
                   # print "span > year not current"
                    year1 = int(dur_split[c+2])
                    month2 = monthDict[dur_split[c+4]]
                    year2 = int(dur_split[c+6])
                    c = len(dur_split)                    
                   # print dur_split, month1, month2, year1, year2
                    break
                
                else:
                    print "Time period not found"

        print dur_split, month1, month2, year1, year2
        temp_duration = (year2 - year1) * 12 - month1 + month2
        total_duration += temp_duration
   # print "total_duration, dose", total_duration, dose_num
    return total_duration, dose_num
#get_efficacy()


# In[70]:

data = {}
cycle_drugs()



