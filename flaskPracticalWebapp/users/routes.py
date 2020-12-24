from flask import Blueprint

users = Blueprint("users", __name__)


@users.route('/register', methods=["GET", "POST"])
def register():
    title = "Register"
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(email=form.email.data, password=hashed_password, dob=form.dob.data)

        db.session.add(user)
        db.session.commit()
        practicals = Practical.query.all()
        x = 10
        for practical in practicals:
            practical.user_id = 1
            x+=1
        flash("Your account has been successfully created! Please login.", "success")
        return redirect(url_for('login'))
    return render_template("register.html", title=title, form=form)


@users.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    title = "Login"
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            # [1:] in place as request.args.get returns url with \ included (eg "\profile" rather than just "profile"), url_for takes in name of function.
            return redirect(url_for(next_page[1:])) if next_page else redirect(url_for("home"))


        else:
            flash("Login credentials incorrect. Please check email and password", "danger")
    return render_template("login.html", title=title, form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))



@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    update = False

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_pic(form.picture.data)
            current_user.profile_pic = picture_file
            update = True
        if current_user.fname != form.fname.data or current_user.surname != form.surname.data:
            current_user.fname = form.fname.data
            current_user.surname = form.surname.data
            update = True
        if update:
            db.session.commit()
            flash("Your changes have been saved!", "success")
            return redirect(url_for("profile"))
    elif request.method == "GET":
        form.fname.data = current_user.fname
        form.surname.data = current_user.surname
        form.email.data = current_user.email
    title = f"{current_user.fname} {current_user.surname}"
    if not(title):
        title=f"User Profile"
    profile_pic = url_for('static', filename=f"profile_pics/{current_user.profile_pic}")
    return render_template("profile.html", title=title, form=form, profile_pic=profile_pic)

@users.route('/settings')
@login_required
def settings():
    title = "Settings"
    return render_template("settings.html", title=title)

# add a route for user practicals, consider giving users usernames then leting them view their
# (favourite) practicals using the usersropriate route


@users.route('/reset_password', methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    title = "Forgot Password"
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Please check your email for instructions on how to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title=title, form=form)


@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))


    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))

    title="Reset Password"
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        practicals = Practical.query.all()
        flash("Your password has been sucessfully updated! You are now able to login", "success")
        return redirect(url_for('login'))
    return render_template("reset_token.html", title=title, form=form)
