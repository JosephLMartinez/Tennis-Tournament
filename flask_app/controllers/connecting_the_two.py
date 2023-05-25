from flask_app import app, Flask
from flask import render_template, redirect, session, request, flash
from flask_app.models.player import Player
from flask_app.models.admin import Admin
from flask_app.models.tournament import Tournament

# checks for existing tournaments and directs you there or if none starts you on making a new one
@app.route("/admins")
def admin_page():
    if not session['user']:
        return redirect('/')
    if not Admin.get_tournament(session['user']):
        return render_template("create_tournament.html")
    my_tournament=[Admin.get_tournament(session['user'])]
    return render_template("my_tournament.html", my_tournament=my_tournament)

# it takes the info and sends it to tournaments table in SQL
@app.route("/new_tournament_available", methods=["POST"])
def make_a_tournament():
    if not session['user']:
        return redirect('/')
    if not Tournament.validate_tournament_posting(request.form):
        print("flash message")
        return redirect('/admins')
    response="No"
    data={
        "admin_id":session['user'],
        "tournament_name": request.form["tournament_name"],
        "state": request.form["state"],
        "city": request.form['city'],
        "low_age": request.form['low_age'],
        "high_age": request.form['high_age'],
        "start_date": request.form['start_date'],
        "end_date": request.form['end_date'],
    }
    # print(data['player_id'])
    Tournament.save(data)
    return redirect("/status")

# shows you the tournament you have
@app.route("/status")
def status():
    if not session['user']:
        return redirect('/')
    my_tournament= [Admin.get_tournament(session['user'])]
    return render_template("my_tournament.html", my_tournament=my_tournament)

@app.route("/players")
def player_index():
    if not session['user']:
        return redirect('/')
    # checks to see if they are in a tournament if no they get to see tournaments
    if not Player.get_tournament_id(session['user']):
        session['age']=Player.get_age(session['user'])
        available_tournaments=Tournament.get_all(session['age'])
        return render_template("available_tournaments.html", available_tournaments=available_tournaments)
    # shows them their scheduled tournament
    my_tournament=Player.get_tournament_id(session['user'])
    tournament_players=Tournament.get_players(my_tournament)
    number_of_players=len(tournament_players)
    variable=1
    bracket_size=[]
    while number_of_players>=2*variable:
        variable=variable*2
        bracket_size.append(variable)
        print(variable)
    bracket_size=list(reversed(bracket_size))
    print(bracket_size)
    round_one=bracket_size
    # while number_of_players>2**variable:
    #     variable=variable+1
    # bracket_size=2**variable
    return render_template("my_tournament.html", tournament_players=tournament_players, bracket_size=bracket_size, round_one=round_one,number_of_players=number_of_players )

# claims the tournament and shows you the bracket
@app.route("/claim_tournament/<int:num>")
def join_tournament(num):
    if not session['user']:
        return redirect('/')
    data={
        "id": session['user'],
        "tournament_id":num
    }
    # adds the tournament to the player
    Player.claim(data)
    # shows them their scheduled tournament
    my_tournament=Player.get_tournament_id(session['user'])
    tournament_players=Tournament.get_players(my_tournament)
    number_of_players=len(tournament_players)
    variable=1
    bracket_size=[1]
    while number_of_players>=2*variable:
        variable=variable*2
        bracket_size.append(variable)
        print(variable)
    bracket_size=list(reversed(bracket_size))
    print("b-size:", bracket_size)
    round_one=bracket_size
    # while number_of_players>2**variable:
    #     variable=variable+1
    # bracket_size=2**variable
    return render_template("my_tournament.html", tournament_players=tournament_players, bracket_size=bracket_size, round_one=round_one,number_of_players=number_of_players)

# If you can no longer attend the tournament
@app.route("/leave_tournament")
def edit_appointment():
    if not session['user']:
        return redirect('/')
    if not session['user']:
        return redirect('/')
    Player.unclaim(session['user'])
    available_tournaments=Tournament.get_all(session['age'])
    return render_template("available_tournaments.html", available_tournaments=available_tournaments)
















# takes the new info from the updated appointment and UPDATES IT
@app.route("/edit", methods=['POST'])
def add_appointment_changes():
    if not session['user']:
        return redirect('/')
    if not Tournament.validate_tournament_posting(request.form):
        print("flash message")
        my_tournament= [Admin.get_tournament(session['user'])]
        return render_template("edit_appointment.html", my_tournament=my_tournament)
    data={
        "admin_id":session['user'],
        "tournament_name": request.form["tournament_name"],
        "start_date": request.form['start_date'],
        "end_date": request.form['end_date']
    }
    Tournament.update(data)
    return redirect("/status")
    
# it deletes the appointment when the customer changes their mind
@app.route("/delete_appointment")
def delete():
    if not session['user']:
        return redirect('/')
    Tournament.delete(session['user'])
    return redirect("/admins")


# Where they find unclaimed appointments
@app.route("/appointments/new")
def unclaimed_appointments():
    if not session['user']:
        return redirect('/')
    available_tournaments=Tournament.get_all(session['age'])
    return render_template("available_tournaments.html", available_tournaments=available_tournaments)


# when a player unselects an assignment it resposts to the unclaimed board
@app.route("/unselect/<int:num>")
def unselect(num):
    if not session['user']:
        return redirect('/')
    data={
        "id": num,
        # "player_id":session['user']
        "player_id":None

    }
    Tournament.unselect(data)
    my_appointments=Tournament.get_all_of_mine(session['user'])
    return render_template("show_my_appointments.html", my_appointments=my_appointments)

# when a player finishes an assignment it should show on the status screen for the client
@app.route("/finished_assignment/<int:num>")
def finished_assignment(num):
    if not session['user']:
        return redirect('/')
    response="Yes"
    data={
        "id": num,
        "finished":response
    }
    Tournament.finished_assignment(data)
    my_appointments=Tournament.get_all_of_mine(session['user'])
    return render_template("show_my_appointments.html", my_appointments=my_appointments)


@app.route("/players/<int:num>")
def player_one_player(num):
    if not session['user']:
        return redirect('/')
    one_player =[Player.get_player(num)]
    return render_template("player_player.html", players=one_player)



@app.route("/players/<int:num>/edit")
def player_edit_screen(num):
    if not session['user']:
        return redirect('/')
    one_player= [Player.get_one(num)]
    return render_template("edit_player.html", the_player=one_player)

@app.route("/edit/<int:num>", methods=["POST"])
def edit_player(num):
    if not Player.validate_player(request.form):
        print("flash message")
        return redirect('/players/new')
    data={
        "id":num,
        "admin_id":session['user'],
        "player_name": request.form["player_name"],
        "description": request.form["description"],
        "network": request.form['network'],
        "release_date": request.form['release_date']
    }
    Player.update(data)
    return redirect("/players")


@app.route("/delete/<int:num>")
def delete_player(num):
    if not session['user']:
        return redirect('/')
    Player.delete(num)
    return redirect('/players')


