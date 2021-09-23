
class Login extends React.Component {

  login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    this.props.socket.emit('login', {custom_email: email, custom_password: password});
  }

  signup() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    let display_name = prompt("Enter your display name:", "");
    if (display_name == "") {
      alert("Display name can't be empty string");
      return;
    } else if (display_name == null) {
      return;
    }

    this.props.socket.emit('signup', {
      custom_email: email, 
      custom_password: password,
      custom_display_name: display_name
    });
  }

  render () {
    return (
      <div className="login_block" id="login_block">
        <h2>Log into Lax</h2>

        <div className="email_div">
          <label htmlFor="email"><b>Email </b></label>
          <input id="email" placeholder="Enter email"></input>
        </div>

        <div className="password_div">
          <label htmlFor="password"><b>Password </b></label>
          <input type="password" id="password" placeholder="Enter password"></input>
        </div>

        <div className="signup_button_div">
          <button onClick={()=>this.signup()}>Signup</button>
        </div>
        <div className="login_button_div">
          <button onClick={()=>this.login()}>Login</button>
        </div>
      </div>
    );
  }
}

export default Login;
