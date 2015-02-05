'''
Created on Jan 8, 2014

@author: sergio
'''
# -*- coding: utf-8 -*-

import web
from web import form
import NeuroDB.neurodb as neurodb
import neodb.core
import datetime
import forms
import model
import config
import shutil

NDB = None

### Url mappings
urls = (
    '/', 'Index',
    '/project', 'Project',
    '/individual', 'Individual',
    '/createIndividual', 'CreateIndividual',
    '/showIndividual', 'ShowIndividual',
    '/showProject', 'ShowProject',
    '/findIndividual', 'FindIndividual',
    '/findProject', 'FindProject',
)

### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates', base='base', globals=t_globals)

class Index:
    def GET(self):
        """ Show page """
        return render.index()

class SaveSession:
    def GET(self):
        pass
    def POST(self):
        pass

####### INDIVIDUAL ########
class Individual:
    def POST(self):
        selection = web.input()
        if 'Create' in selection:
            web.seeother('/createIndividual')
        if 'Find' in selection:
            web.seeother('/findIndividual')

    def GET(self):
        form = forms.project()
        return render.project(form)

class CreateIndividual():
    def GET(self):
        form = forms.create_individual
        return render.createIndividual(form)
    
    def POST(self):
        conn = neurodb.connect_db()
        x = web.input(Picture={})
        filedir = config.TMP_DIR
        if 'Picture' in x:
            filepath=x.Picture.filename.replace('\\','/')
            filename=filepath.split('/')[-1]
            fout = open(filedir +'/'+ filename,'w')
            fout.write(x.Picture.file.read())
            fout.close()
        
            id_individual = neurodb.create_individual(x['Name'], x['Description'], str(x['Birth Date']), filedir +'/'+ filename)
        web.seeother('/showIndividual?id=%s'%(id_individual))
        
class ShowIndividual():
    def GET(self):
        w = web.input()
        if w.has_key('id'):
            individual = neurodb.get_individual(w['id'])
            picture = None
            if individual['picture_path'] != None:
                shutil.copy(individual['picture_path'], '/home/sergio/iibm/workspace2/NeuroDB/src/NeuroDB/WebUI/static')
                picture = individual['picture_path'].split('/')[-1]
            return render.showIndividual(individual, picture)
    
    def POST(self):
        w = web.input()
        individual = []
        
        return render.showIndividual(individual)

class FindIndividual():
    def GET(self):
        msg = ''
        form = forms.find_individual
        individuals = []
        w = web.input()
        if w.has_key('msg'):
            msg = w['msg']
        
        return render.findIndividual(form, individuals, msg)
    
    def POST(self):
        msg = ''
        refer = web.ctx.env.get('HTTP_REFERER')
        w = web.input()
        if refer.split('/')[-1] == 'findIndividual' and w.has_key('individual'):
            id_individual = w['individual']
            web.seeother('/showIndividual?id=%s'%(id_individual))
            return
        
        if w['Name'] == '':
            iname = None
        else:
            iname = str(w['Name'])
        
        if w['Birth Date from'] == '':
            bdate_start = None
        else:
            bdate_start = str(w['Birth Date from'])
            
        if w['to'] == '':
            bdate_end = None
        else:
            bdate_start = str(w['to'])
        
        individuals = neurodb.find_individual(name = iname, birth_date_from = bdate_start,
                                birth_date_end = bdate_end)
        if individuals != []:
            form = None
            return render.findIndividual(form, individuals, msg)
        else:
            web.seeother('/findIndividual?msg=noindividual')
    

####### PROJECT #######
class CreateProject:
    def POST(self):
        form = forms.create_project
        if not form.validates():
            return render.createProject(form)
        else:
            name = form.d.Name 
            #TODO: reformatear la fecha que ingresa el usuario y cargar esa fecha
            date = datetime.date.today()
            description = form.d.Description
               
            id_project = neurodb.create_project(name, date, description)
            web.seeother('/saveSession?id=%s'%id_project)

    def GET(self):
        form = forms.create_project
        return render.createProject(form)

class Project:
    def POST(self):
        selection = web.input()
        if 'Create' in selection:
            web.seeother('/createProject')
        if 'Find' in selection:
            web.seeother('/findProject')

    def GET(self):
        form = forms.project()
        return render.project(form)

class FindProject():
    def GET(self):
        msg = ''
        form = forms.find_project
        projects = []
        w = web.input()
        if w.has_key('msg'):
            msg = w['msg']
        
        return render.findProject(form, projects, msg)
    
    def POST(self):
        msg = ''
        refer = web.ctx.env.get('HTTP_REFERER')
        w = web.input()
        if refer.split('/')[-1] == 'findProject' and w.has_key('project'):
            id_project = w['project']
            web.seeother('/showProject?id=%s'%(id_project))
            return
        
        if w['Name'] == '':
            iname = None
        else:
            iname = str(w['Name'])
        
        if w['Date from'] == '':
            date_start = None
        else:
            date_start = str(w['Date from'])
            
        if w['to'] == '':
            date_end = None
        else:
            date_start = str(w['to'])
        
        projects = neurodb.find_project(name = iname, date_from = date_start,
                                date_end = date_end)
        if projects != []:
            form = None
            return render.findProject(form, projects, msg)
        else:
            web.seeother('/findProject?msg=noproject')

class ShowProject():
    def GET(self):
        w = web.input()
        if w.has_key('id'):
            project = neurodb.get_project(w['id'])
            return render.showProject(project)
    
    def POST(self):
        w = web.input()
        project = []
        
        return render.showProject(project)



if __name__ == '__main__':
    neurodb.connect_db()
    app = web.application(urls, globals())
    app.run()
    pass