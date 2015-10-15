from GenericInventory import app, db
from flask import render_template, url_for, request, Flask, redirect, flash
from database import Sample, Container, Aliquot
import datetime


@app.route('/')
@app.route('/samples')
def samples():
    """
    Home page for sample viewing
    """
    samples = Sample.query.order_by(Sample.sampleId.desc())
    return render_template("samples.html", samples=samples)


@app.route('/requests')
@app.route('/requests/<sampleName>')
def requests(sampleName=None):
    """
    Page for viewing a table of requests
    """
    if sampleName:
        requests = Aliquot.query.filter(Aliquot.sampleName == sampleName).\
            order_by(Aliquot.aliquotId.desc())
    else:
        requests = Aliquot.query.order_by(Aliquot.aliquotId.desc())
    return render_template("requests.html", requests=requests)


@app.route('/containers')
@app.route('/containers/<sampleName>')
def containers(sampleName=None):
    """
    Page for viewing containers.
    If sampleName specified, will only show those containers tied to sampleName
    """
    if sampleName:
        containers = Container.query.\
            filter(Container.sampleName == sampleName).\
            order_by(Container.containerId)
    else:
        containers = Container.query.order_by(Container.containerId.desc())
    return render_template("containers.html", containers=containers)


@app.route('/query', methods=['GET', 'POST'])
def query():
    """
    GET: Page for filling in information to query
    POST: Show a table of queried info
    """
    if request.method == 'GET':
        return render_template("query.html")
    elif request.method == 'POST':
        samples = Sample.query
        for column in request.form:
            if column != 'checked' and request.form[column]:
                samples = samples.filter(getattr(Sample, column).ilike("%" + request.form[column] + "%"))
        # Get list of checked checkboxes
        headers = request.form.getlist('checked')
        return render_template("samples.html", samples=samples, headers=headers)


@app.route('/delete/<item>', methods=['POST'])
def delete(item):
    """
    POST: Delete selected checkbox items
    """
    checked = request.form.getlist('checked')
    if item == 'sample':
        for sampleId in checked:
            sample = Sample.query.filter(Sample.sampleId == sampleId).first()
            db.session.delete(sample)
        else:
            db.session.commit()
            flash("Successfully deleted samples")
            return redirect(url_for('samples'))
    elif item == 'container':
        for containerId in checked:
            container = Container.query.filter(Container.containerId == containerId).first()
            db.session.delete(container)
        else:
            db.session.commit()
            flash("Successfully deleted containers")
            return redirect(url_for('containers'))
    elif item == 'request':
        for aliquotId in checked:
            aliquot = Aliquot.query.filter(Aliquot.aliquotId == aliquotId).first()
            # If you delete a request, I add the amount back to the conatiner
            # Delete the container lines if unwanted
            container = Container.query.filter(Container.containerId == aliquot.containerId).first()
            container.amount += aliquot.amount
            db.session.delete(aliquot)
            db.session.flush()
        else:
            db.session.commit()
            flash("Successfully deleted requests")
            return redirect(url_for('requests'))


@app.route('/addSample', methods=['GET', 'POST'])
def addSample():
    """
    GET: Page for adding sample information and location information
    POST: Add the information into the database
    """
    if request.method == 'GET':
        return render_template("addSample.html")
    else:
        # Put all forms in a dictionary, changing "" inputs to None
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        sample = Sample()
        # For these for loops to work, input forms MUST be named the same as
        # the database columns
        for column in formDict:
            setattr(sample, column, formDict[column])
        sample.date = "{}-{}-{}".format(datetime.date.today().year,
                                        datetime.date.today().month,
                                        datetime.date.today().day)
        db.session.add(sample)
        db.session.commit()
        flash("Successfully added sample")
        return redirect(url_for('addSample'))


@app.route('/editSample/<sampleId>', methods=['GET', 'POST'])
def editSample(sampleId):
    """
    GET: Page for editing sample fields
    POST: Edits the sample information
    """
    sample = Sample.query.filter(Sample.sampleId == sampleId).first()
    if request.method == 'GET':
        return render_template('editSample.html', sample=sample)
    elif request.method == 'POST':
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        # if sampleName is different, go through aliquots and containers and change as well
        if formDict['sampleName'] != sample.sampleName:
            containers = Container.query.filter(Container.sampleName == sample.sampleName)
            for container in containers:
                container.sampleName = formDict['sampleName']
            aliquots = Aliquot.query.filter(Aliquot.sampleName == Sample.sampleName)
            for aliquot in aliquots:
                aliquot.sampleName = formDict['aliquot']
        for column in formDict:
            setattr(sample, column, formDict[column])
        db.session.commit()
        flash("Successfully edited sample")
        return redirect(url_for('samples'))


@app.route('/addRequest', methods=['GET', 'POST'])
@app.route('/addRequest/<sampleName>', methods=['GET', 'POST'])
def addRequest(sampleName=None):
    """
    GET: Page for filling in information about a request
    POST: Adds the request into the database from form information
    """
    if request.method == 'GET':
        if sampleName:
            return render_template('addRequest.html', sampleName=sampleName, prev=None)
        else:
            return render_template('addRequest.html', prev=None)
    else:
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        aliquot = Aliquot()
        for column in formDict:
            setattr(aliquot, column, formDict[column])
        db.session.add(aliquot)
        # Adjust container volume, no amountUnits logic yet, it would go here
        containerId = request.form['containerId']
        container = Container.query.filter(Container.containerId == containerId).first()
        container.amount -= float(request.form['amount'])
        db.session.commit()
        flash("Successfully added request")
        return redirect(url_for('addRequest', sampleName=request.form['sampleName']))


@app.route('/chooseContainer', methods=['POST'])
def chooseContainer():
    """
    After editing request, post request to show choosable containers
    """
    containers = Container.query.filter(Container.sampleName == request.form['sampleName']).\
                                 filter(Container.amount >= request.form['amount'])
    # No available containers for the specified amount
    if containers.count() == 0:
        return render_template('chooseContainer.html',
                               empty=True,
                               prev=request.form)
    return render_template('chooseContainer.html',
                           containers=containers,
                           prev=request.form)


@app.route('/editRequest/<int:aliquotId>', methods=['GET', 'POST'])
def editRequest(aliquotId):
    """
    GET: Page for editing fields about a request
    POST: Edits the request
    """
    aliquot = Aliquot.query.filter(Aliquot.aliquotId == aliquotId).first()
    container = Container.query.filter(Container.containerId == aliquot.containerId).first()
    existingAmount = container.amount + aliquot.amount
    existingUnits = container.amountUnits
    if request.method == 'GET':
        return render_template('editRequest.html', aliquot=aliquot,
                               existingAmount=existingAmount, existingUnits=existingUnits)
    elif request.method == 'POST':
        # Check if you can edit within bounds of container
        # No amountUnits logic yet, it would go here
        if float(request.form['amount']) > float(existingAmount):
            flash("Delivery amount greater than existing amount")
            return render_template('editRequest.html', aliquot=aliquot,
                                   existingAmount=existingAmount,
                                   existingUnits=existingUnits, error=True)
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        for column in formDict:
            setattr(aliquot, column, formDict[column])
        container.amount = float(existingAmount) - float(request.form['amount'])
        db.session.commit()
        flash("Request successfully edited")
        return redirect(url_for('requests'))


@app.route('/addContainer', methods=['GET', 'POST'])
@app.route('/addContainer/<sampleName>', methods=['GET', 'POST'])
def addContainer(sampleName=None):
    if request.method == 'GET':
        if sampleName:
            return render_template("addContainer.html", sampleName=sampleName, prev=None)
        else:
            return render_template("addContainer.html", prev=None)
    elif request.method == 'POST':
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        sample = Sample.query.filter(Sample.sampleName == formDict['sampleName']).first()
        if sample is None:
            flash("Sample Name not found")
            return render_template("addContainer.html", prev=formDict, error=True)
        container = Container()
        for column in formDict:
            setattr(container, column, formDict[column])
        container.date = "{}-{}-{}".format(datetime.date.today().year,
                                           datetime.date.today().month,
                                           datetime.date.today().day)
        db.session.add(container)
        db.session.commit()
        flash("Successfully added container")
        return redirect(url_for('addContainer', sampleName=request.form['sampleName']))


@app.route('/editContainer/<containerId>', methods=['GET', 'POST'])
def editContainer(containerId):
    """
    GET: Page view for editing a container
    """
    container = Container.query.filter(Container.containerId == containerId).first()
    if request.method == 'GET':
        return render_template('editContainer.html', container=container)
    elif request.method == 'POST':
        formDict = {}
        for column in request.form:
            if not request.form[column]:
                formDict[column] = None
            else:
                formDict[column] = request.form[column]
        for column in formDict:
            setattr(container, column, formDict[column])
        db.session.commit()
        flash("Successfully edited container")
        return redirect(url_for('containers'))
