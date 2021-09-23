
class Channels extends React.Component {

  createNewChannel() {
    var session_token = window.localStorage.getItem('session_token');
    var prompt_msg = ('Enter a channel name\n' + 
                      'Use only numbers, letters and underscores (and no spaces)');
    let channel_name = prompt(prompt_msg, "");

    if (channel_name == null) {
      return;
    }
    var valid = channel_name.match("^[A-Za-z0-9_]+$");
    if (!valid) {
      alert("Channel name not valid");
      return;
    }

    this.props.socket.emit('create', {
      custom_session_token: session_token, 
      custom_channel_name: channel_name
    });
  }


  changeDisplayName() {
    var session_token = window.localStorage.getItem('session_token');
    let display_name = prompt("Enter new display name:", "");
    if (display_name == "") {
      alert("Display name can't be empty string");
      return;
    } else if (display_name == null) {
      return;
    }

    this.props.socket.emit('change_display_name', {
      custom_session_token: session_token, 
      custom_display_name: display_name
    });
  }


  changeEmail() {
    var session_token = window.localStorage.getItem('session_token');
    let new_email = prompt("Enter new email:", "");
    if (new_email == "") {
      alert("Email can't be empty string");
      return;
    } else if (new_email == null) {
      return;
    }

    this.props.socket.emit('change_email', {
      custom_session_token: session_token, 
      custom_email: new_email
    });
  }


  openChannel(c_name) {
    this.props.channelSetter(c_name);
    if (this.props.currentThread) {
      history.pushState({}, "", "/" + c_name + "/" + this.props.currentThread);
    } else {
      history.pushState({}, "", "/" + c_name);
    }
    this.props.get_msg_func(c_name);
  }


  deleteChannel(c_name) {
    var session_token = window.localStorage.getItem('session_token');
    var answer = window.confirm("Are you sure you want to delete that channel?");
    if (answer) {
      this.props.socket.emit('delete', {
        custom_session_token: session_token, 
        custom_channel_name: c_name
      });      
    }
  }


  render () {
    var session_token = window.localStorage.getItem('session_token');

    const channels = this.props.chan_arr.map((elem) => {
      var del_elem = null;
      if (session_token == elem.creator_token) {
        del_elem = <button id="del_ch_button" onClick={()=>this.deleteChannel(elem.channel_name)}>Delete</button>;
      }
      return (
        <div key={elem.channel_name} id={elem.channel_name} className="channel_element">
          <button onClick={()=>this.openChannel(elem.channel_name)}>{elem.channel_name}</button>
          {del_elem}
          <div className="channel_unread">Unread: {elem.num_unread}</div>
        </div>
      );
    });

    if (this.props.isMobile && (this.props.currentChannel || this.props.currentThread)) {
      return null;
    }

    var cont_width = (this.props.isMobile) ? "95%" : this.props.width;

    return (
      <div className="channels_block" id="channels_block" style={{ width: cont_width }}>
        <div className="channel_list_container">
          <p><b>Channels:</b></p>
          <div id="channel_list">
            {channels}
          </div>
        </div>
        <div className="create_new_channel_button">
          <button onClick={()=>this.createNewChannel()}>Create new channel</button>
        </div>
        <div className="change_display_name_button">
          <button onClick={()=>this.changeDisplayName()}>Change display name</button>
        </div>
        <div className="change_email_button">
          <button onClick={()=>this.changeEmail()}>Change Email</button>
        </div>
        <div className="logout_button">
          <button onClick={()=>this.props.logout()}>Log Out</button>
        </div>
      </div>
    );
  }
}

export default Channels;
