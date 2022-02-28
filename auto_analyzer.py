from operator import mod
from statistics import mode
from unicodedata import category
from flask import Flask, flash,render_template,request,redirect, url_for
import model
import scraper_app
from threading import Thread

app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@ app.route('/')
def index():
    return render_template('index.html')

# &&&&&&&&&  Show & change the working status of task  &&&&&&&&&&

# Show Status of Tasks
@ app.route('/task_status')
def status():
    data=model.view_status()
    return render_template('status.html',data=data)

# To set Running Status
@app.route('/start/<id>', methods=['GET','POST'])
def start(id):
    print(id)
    print('start')
    model.update_status(id,"Running")
    return render_template('test.html')

# To Set Stop Status
@app.route('/pause/<id>', methods=['GET','POST'])
def pause(id):
    print(id)
    print('pause')
    model.update_status(id,"Stop")
    return render_template('test.html')

# $$$$$$$$$   End of Working Status Part   $$$$$$$$$$





# &&&&&&&&&  function to create new task  &&&&&&&&&

# create/store simple details in database
@ app.route('/create')
def create():
    return render_template('create_task.html')

@ app.route('/create_formula',methods =["GET", "POST"])
def create_formula():
    if request.method == "POST":
        name,url,website,category,optional_subcategory='','','','',''
        # getting input with name = fname in HTML form
        name = request.form.get("name")
        url = request.form.get("url")
        website=request.form.get("web")
        category=request.form.get("category")
        optional_subcategory=request.form.get("cat_url")
        print(name,url,website,category,optional_subcategory)
        data={'name':name,'url':url,'website':website,'category':category,'sub_category':optional_subcategory}
        result_id=model.store_task(data)
        return render_template('formula.html',id=result_id)
    else:
        return redirect('/create')

# store formula for task
@app.route('/task_created',methods =["GET", "POST"])
def completion_task_creation():
    if request.method=="POST":
        if request.form.get("finish"):
            id=request.form.get("id").split(':')[-1].strip()

            ebay_fee = request.form.get("ebay_fee")
            ship_fee = request.form.get("ship_fee")
            margin_fee=request.form.get("margin_fee")
            data={'ebay_fee':ebay_fee,'ship_fee':ship_fee,'margin_fee':margin_fee,'id':id}
            model.task_formula(data)
            return render_template("create_task.html",msg=True)
        else:
            return redirect('/create')

# store default formula for task
@app.route("/default_formula/<id>/create")
def defult_formula(id):
    status=model.task_with_default_settings(id)
    if status=="No setting":
        flash("No Default Settings Present!!!")
        return render_template("formula.html",id=id)
    
    if status:
        return render_template("create_task.html",msg=True)
    else:
        return "task not present"

# $$$$$$$$$   End of Task Create Part   $$$$$$$$$$





# &&&&&&&&&&&  Show all tasks list  &&&&&&&&&&&&&

# show list of tasks
@ app.route('/tasks')
def tasks_lists():
    tasks_list=model.get_all_tasks()
    return render_template("tasks.html",tasks_list=tasks_list)

# Delete task
@app.route('/delete/<id>/',methods=['GET','POST'])
def delete(id):
    try:
        status=model.check_task_record(id)
        if status=="1":
            model.delete_task(id)
            tasks_list=model.get_all_tasks()
            return render_template("tasks.html",tasks_list=tasks_list,msg="delete", id=id)
        else:
            tasks_list=model.get_all_tasks()
            return render_template("tasks.html",tasks_list=tasks_list,msg="not delete", id=id)
    except:
        tasks_list=model.get_all_tasks()
        return render_template("tasks.html",tasks_list=tasks_list,msg="not delete", id=id)

# Edit Task
@ app.route('/edit/<id>/',methods =["GET", "POST"])
def edit(id):
    if request.method=="POST":
        name,url,website,category,optional_subcategory='','','','',''
        # getting input with name = fname in HTML form
        name = request.form.get("name")
        url = request.form.get("url")
        website=request.form.get("web")
        category=request.form.get("category")
        optional_subcategory=request.form.get("cat_url")
        print(name,url,website,category,optional_subcategory)
        data={'name':name,'url':url,'website':website,'category':category,'sub_category':optional_subcategory}
        id=request.form.get("id").split(":")[-1].strip()

        ebay_fee = request.form.get("ebay_fee")
        ship_fee = request.form.get("ship_fee")
        margin_fee=request.form.get("margin_fee")
        data.update({'ebay_fee':ebay_fee,'ship_fee':ship_fee,'margin_fee':margin_fee,'id':id})
        model.edit_task(data)
        flash('Task Update Successfully!!!')
        return redirect(url_for('tasks_lists'))
    else:
        data=model.get_specific_record(id)
        return render_template('edit_task.html',id=id,data=data)

# $$$$$$$$$   End of Show Tasks Part   $$$$$$$$$$





# &&&&&&&&&&&  Setting/Integration Part  &&&&&&&&&&&

@ app.route('/settings')
def setting_formula():
    data=model.get_settings()
    return render_template('integration.html',data=data)





@ app.route('/product_data')
def product_data():
    return render_template("scrape_data.html")


@ app.route('/integration_settings',methods=["GET","POST"])
def integration_settings():
    if request.method=="POST":
        username,password='',''
        ebay_fee = request.form.get("ebay_fee")
        ship_fee = request.form.get("ship_fee")
        margin_fee=request.form.get("margin_fee")
        username=request.form.get("username")
        password=request.form.get("password")
        data={'ebay_fee':ebay_fee,'ship_fee':ship_fee,'margin_fee':margin_fee,'username':username,'password':password}
        model.store_settings(data)
        flash('Settings Store Successfully!!!')
        return redirect('/settings')
    else:
        return render_template("integration_settings.html")




if __name__=='__main__':
    
    thread = Thread(target=scraper_app.run_scraper)
    thread.daemon = True
    thread.start()
    app.run(debug=True)