# Please consider the following:
# 1. This script needs to be changed in order to satisfy your html
#    please modify the @step(u'And I start scrolling (\d+) times')
# 2. This script is build to acomodate a page with multiple scrolling
#    elements and with eventually ajax loading
# 3. In order to work, the opened browser page should be keep maximized
# 4. The script is using a mouse over selenium method to perform scrolling
#    This method I have found it to give results closer to reality, as
#    ussualy people tend to scroll with the mouse weel, which eventually
#    has also a mouse over event (and also mouse out)

from lettuce import before, world, step
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging
import numpy
from perf_util import predifined 

logging.basicConfig(filename='perf.log',level=logging.INFO)


@before.all
def setup_browser():
    logging.info("Start new test with Firefox")  
    world.driver = webdriver.Firefox()
    world.driver.maximize_window()
    

@step(u'Given I have initial setup')
def parse_params_of_argv(step):
    #add here any other setup you want
    pass    
    

@step(u'When I go to login page')
def given_i_go_to_loginpage(step):
   world.driver.get(predifined['login_url'])


@step(u'And I fill in the credentials fields "([^"]*)" "([^"]*)"')
def input_user(step, id1,id2):
    el = world.driver.find_element_by_id(id1)
    el.send_keys(predifined[id1])
    el = world.driver.find_element_by_id(id2)
    el.send_keys(predifined[id2])	


@step(u'And I submit')
def submit_pass(step):
    button = world.driver.find_element_by_class_name("btn-red")
    button.click()
    world.driver.execute_script('window.focus();')
    # wait for the magic login cookie    
    time.sleep(10)
    

@step(u'And I go to the check page')
def submit_pass(step):
    world.driver.get(predifined['check_url'])
    world.driver.execute_script('window.focus();')
    # wait for all to load
    time.sleep(10)       


@step(u'And I insert the fps javascript')
def javascript_insert_pass(step):
    # insert the magic javascript
    with open(predifined['local_javascript_url']) as f:
        content = f.readlines()
    js = "".join(content)
    javascript = "\
        var doc = window.document;\
        var script = doc.createElement(\"script\");\
        script.innerHTML=\"%s\";\
        doc.body.appendChild(script);" % (js.strip()\
            .replace('\t','').replace("\n", "").replace('"','\\"'))
    #logging.info("javascript = "+javascript)
    world.driver.execute_script(javascript)
    

@step(u'And I scroll (\d+) times to ensure data is loaded')
def scroll(step, times):
    #perform initial scrolling
    for x in range(0, int(times)):
        for div in range (0,predifined['number_of_widgets']):                
            world.driver.execute_script('document.getElementsByClassName\
                ("mention-container-wrapper")[%d].getElementsByClassName("mentions")\
                [0].getElementsByTagName("ul")[0].scrollTop = %d ' % (div,x * predifined['scroll_step']))
            logging.info("scrolling widget: %d for %d time" % (div,x))
    
    elems = []    
    #insert id on each element for easy retrieval
    for div in range (0,predifined['number_of_widgets']):
        elems.append(world.driver.execute_script('return document.\
            getElementsByClassName("mention-container-wrapper")[%d].\
            getElementsByClassName("mentions")[0].getElementsByTagName("ul")[0].\
            children.length' % (div)))
        world.driver.execute_script('document.getElementsByClassName\
                ("mention-container-wrapper")[%d].getElementsByClassName("mentions")\
                [0].getElementsByTagName("ul")[0].id = "ul_scroll_%d"' % (div,div))
        for li in range(0, elems[div]):
            world.driver.execute_script('document.getElementsByClassName\
                ("mention-container-wrapper")[%d].getElementsByClassName("mentions")\
                [0].getElementsByTagName("ul")[0].children[%d].id = "ul_scroll_%d_%d"' % (div,li,div,li))
        logging.info("number of elements in widget[%d]: %d" % (div,elems[div]))
    
    #extract the elements we need to hover over
    li_hover = []
    for div in range (0,predifined['number_of_widgets']):
        element_to_hover_over = world.driver.find_element_by_id("ul_scroll_%d" % (div))
        li_hover.append([])
        for li in range(0, elems[div]):
            element_to_hover_over = world.driver.find_element_by_id("ul_scroll_%d_%d" % (div,li))
            li_hover[div].append(element_to_hover_over)
    
    #start logging
    world.driver.execute_script('insertIntoFpsArr = true');
    for div in range (0,predifined['number_of_widgets']):
        for li in range(0, elems[div]):
            ActionChains(world.driver).move_to_element(li_hover[div][li]).perform()

@step(u'And I scroll again to extract the fps values')
def fps_values(step):
    world.fps_values = world.driver.execute_script("return fps_arr")


@step(u'Then the avarage fps valus should be over (\d+)')
def avarage_lookup(step,avg):
    mean = numpy.mean(world.fps_values)    
    std = numpy.std(world.fps_values)   
    logging.info("numpy mean: %d ,std: %d" % (mean,std))
    logging.info("values are: %s " % (world.fps_values))
    assert mean > avg

