import Login from "/static/components/login.js";
import Channels from "/static/components/channels.js";
import Chats from "/static/components/chats.js";
import Thread from "/static/components/thread.js";


class Lax extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoggedIn: false,
      isMobile: false,
      cur_channel: "",
      cur_thread: "",
      chan_arr: Array(),
      msg_arr: Array(),
      replies_map: {
        channel_name: "", 
        main_msg: {body: "", display_name: ""}, 
        replies: Array()
      },
    };
    this.socket = io();
  }

  loginSetter(bool) {
    this.setState({isLoggedIn: bool});
  }

  channelSetter(str) {
    this.setState({cur_channel: str});
  }

  threadSetter(str) {
    this.setState({cur_thread: str});
  }

  logout() {
    window.localStorage.removeItem("session_token");
    history.pushState({}, "", "/");
    // isMobile is not reset
    this.setState({
      isLoggedIn: false, 
      cur_channel: "",
      cur_thread: "",
      chan_arr: Array(),
      msg_arr: Array(),
      replies_map: {
        channel_name: "", 
        main_msg: {body: "", display_name: ""}, 
        replies: Array()
      },
    });
  }

  returnToChannels() {
    this.setState({
      cur_channel: "",
      cur_thread: "",
      msg_arr: Array(),
      replies_map: {
        channel_name: "", 
        main_msg: {body: "", display_name: ""}, 
        replies: Array()
      },
    });
    history.pushState({}, "", "/");
  }

  getChannels() {
    var session_token = window.localStorage.getItem('session_token');
    this.socket.emit('get_channels', {custom_session_token: session_token});
  }

  getMessages(chan_name) {
    if (!chan_name) {
      return;
    }

    var session_token = window.localStorage.getItem('session_token');

    this.socket.emit('get_messages', {
      custom_session_token: session_token, 
      custom_channel_name: chan_name
    });
  }

  getReplies(msg_id) {
    if (!msg_id) {
      return;
    }

    var session_token = window.localStorage.getItem('session_token');

    this.socket.emit('get_replies', {
      custom_session_token: session_token,
      custom_msg_id: msg_id
    });
  }


  getContent(channel, thread) {
    if (this.state.isLoggedIn) {
      this.getChannels();
      this.getMessages(channel);
      this.getReplies(thread);
    }
  }


  getPathAndSetState() {
    var pathname = document.location.pathname;
    var paths = pathname.split("/");
    var thread = "";
    if (paths.length > 2) {
      thread = paths[2];
    }
    this.channelSetter(paths[1]);
    this.threadSetter(thread);
    this.getContent(paths[1], thread);
  }


  componentDidMount() {
    this.getPathAndSetState();

    this.socket.on('connect', () => {
      var session_token = window.localStorage.getItem('session_token');
      this.socket.emit('check_token', {custom_session_token: session_token});
    });

    this.socket.on('check_token_response', (data) => {
      if (data.status) {
        this.loginSetter(true);
      } else {
        console.log('token was not valid on check');
      }
      this.getContent(this.state.cur_channel, this.state.cur_thread);
    });

    this.socket.on('login_response', (data) => {
      if (data.status) {
        window.localStorage.setItem("session_token", data.session_token);
        this.loginSetter(true);
        this.getContent(this.state.cur_channel, this.state.cur_thread);
      } else {
        alert("login failed");
        this.logout();
      }
    });

    this.socket.on('signup_response', (data) => {
      if (data.status) {
        window.localStorage.setItem("session_token", data.session_token);
        this.loginSetter(true);
        this.getChannels();
      } else {
        alert("signup failed");
        this.logout();
      }
    });

    this.socket.on('create_response', (data) => {
      if (data.status) {
        this.getChannels();
      } else {
        console.log("failed to create channel");
        alert("failed to create channel");
      }
    });

    this.socket.on('delete_response', (data) => {
      if (data.status) {
        if (this.state.cur_channel == data.del_channel) {
          this.threadSetter("");
          this.channelSetter("");
          history.pushState({}, "", "/");
        }
        this.getChannels();
      } else {
        console.log("failed to delete channel");
        alert("failed to delete channel");
      }
    });

    this.socket.on('get_channels_response', (data) => {
      if (data.status) {
        this.setState({chan_arr: data.result});
      } else {
        console.log("failed to get channels");
      }
    });

    this.socket.on('get_messages_response', (data) => {
      if (data.status) {
        this.setState({msg_arr: data.result});
        this.getChannels();
      } else {
        console.log("failed to get messages");
      }
    });

    this.socket.on('get_replies_response', (data) => {
      if (data.status) {
        this.setState({replies_map: {
          channel_name: data.channel_name,
          main_msg: data.main_msg,
          replies: data.replies,
          }
        });
        if (this.state.cur_channel == data.channel_name) {
          this.getMessages(data.channel_name);
        }
      } else {
        console.log("failed to get replies");
      }
    });

    this.socket.on('post_messages_response', (data) => {
      if (data.status) {
        this.getMessages(this.state.cur_channel);
        this.getChannels();
      } else {
        console.log("failed to post message");
      }
    });

    this.socket.on('post_reply_response', (data) => {
      if (data.status) {
        this.getReplies(this.state.cur_thread);
        this.getMessages(this.state.cur_channel);
      } else {
        console.log("failed to post reply");
      }
    });

    this.socket.on('change_display_name_response', (data) => {
      if (data.status) {
        this.getContent(this.state.cur_channel, this.state.cur_thread);
      } else {
        console.log("failed to change display name");
      }
    });

    this.socket.on('change_email_response', (data) => {
      if (data.status) {
        alert("Email changed");
      } else {
        alert("Failed to change email");
      }
    });
    

    const media = window.matchMedia('(max-width: 600px)');
    if (media.matches) {
      this.setState({isMobile: true});
    } else {
      this.setState({isMobile: false});
    }

    window.addEventListener("popstate", () => { 
      this.getPathAndSetState();
    });

    media.addEventListener('change', (e) => {
      let mobile = e.matches;
      if (mobile) {
        this.setState({isMobile: true});
      } else {
        this.setState({isMobile: false});
      }
    });
  }

  componentWillUnmount() {
    this.socket.close();
  }


  render() {    
    const isLoggedIn = this.state.isLoggedIn;
    const isMobile = this.state.isMobile;
    const current_channel = this.state.cur_channel;
    const current_thread = this.state.cur_thread;

    return (
      <div className={isMobile ? "lax_mobile" : "lax_wide"}>
        {isLoggedIn && isMobile && (current_channel || current_thread) &&
          <div className="return_button" id="return_button">
            <button onClick={()=>this.returnToChannels()}>Return to channels</button>
          </div>
        }
        {!isLoggedIn && <Login 
                          socket={this.socket}
                        />
        }
        {isLoggedIn && <Channels
                          logout={() => this.logout()}
                          channelSetter={(s) => this.channelSetter(s)}
                          get_msg_func={(s) => this.getMessages(s)}
                          currentChannel={current_channel}
                          currentThread={current_thread}
                          chan_arr={this.state.chan_arr}
                          isMobile={isMobile}
                          width={"20%"}
                          socket={this.socket}
                        />
        }
        {isLoggedIn && current_channel && !current_thread &&
          <Chats currentChannel={current_channel}
            currentThread={current_thread}
            threadSetter={(s) => this.threadSetter(s)}
            get_replies_func={(s) => this.getReplies(s)}
            msg_arr={this.state.msg_arr}
            isMobile={isMobile}
            width={"75%"}
            socket={this.socket}
          />
        }
        {isLoggedIn && current_channel && current_thread &&
          <Chats currentChannel={current_channel}
            currentThread={current_thread}
            threadSetter={(s) => this.threadSetter(s)}
            get_replies_func={(s) => this.getReplies(s)}
            msg_arr={this.state.msg_arr}
            isMobile={isMobile}
            width={"45%"}
            socket={this.socket}
          /> 
        }
        {isLoggedIn && current_channel && current_thread &&
          <Thread 
            currentChannel={current_channel}
            currentThread={current_thread}
            replies_map={this.state.replies_map}
            threadSetter={(s) => this.threadSetter(s)}
            isMobile={isMobile}
            width={"30%"}
            socket={this.socket}
          />
        }
      </div>
    );
  }
}

export default Lax;
