
class Thread extends React.Component {

  postReply() {
    let message = document.getElementById("thread_comment_id").value;
    if (!message) {
      return;
    }
    var session_token = window.localStorage.getItem('session_token');
    var msg_id = this.props.currentThread;
    
    this.props.socket.emit('post_reply', {
      custom_session_token: session_token,
      custom_msg_id: msg_id,
      custom_message: message
    });

    document.getElementById("thread_comment_id").value = "";
  }


  closeThread() {
    this.props.threadSetter("");
    history.pushState({}, "", "/" + this.props.currentChannel);
  }

  render () {

    const replies = this.props.replies_map.replies.map((elem) =>
      <div className="thread_message" key={elem.msg_id} id={"msg_id_" + elem.msg_id}>
        <div><b>{elem.display_name}</b></div>
        <div className="thread_body">{elem.body}</div>
      </div>
    );

    var cont_width = (this.props.isMobile) ? "95%" : this.props.width;

    return (
      <div className="thread" id="thread" style={{ width: cont_width }}>

        <div className="current_thread">
          <p id="current_thread_parag">
            <b>Thread</b> {this.props.replies_map.channel_name} 
            <button id="close_thread_button" onClick={()=>this.closeThread()}>X</button>
          </p>
        </div>

        <div id="thread_main_message_container">
          <div className="thread_message" id="msg_main">
            <div><b>{this.props.replies_map.main_msg.display_name}</b></div>
            <div className="thread_body">{this.props.replies_map.main_msg.body}</div>
            <hr />
          </div>
        </div>

        <div className="thread_chat">
          <div className="thread_messages" id="thread_messages">
            {replies}
          </div>

          <div className="thread_comment_box">
            <input name="thread_comment" id="thread_comment_id"></input>
            <button onClick={()=>this.postReply()}>Post</button>
          </div>
        </div>

      </div>
    );
  }
}

export default Thread;
