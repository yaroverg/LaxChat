
class Chats extends React.Component {

  postMessage() {
    let message = document.getElementById("current_channel_comment_id").value;
    if (!message) {
      return;
    }
    var session_token = window.localStorage.getItem('session_token');
    var chan_name = this.props.currentChannel;
    
    this.props.socket.emit('post_messages', {
      custom_session_token: session_token,
      custom_channel_name: chan_name,
      custom_message: message
    });

    document.getElementById("current_channel_comment_id").value = "";
  }

  showThread(m_id) {
    var str_m_id = m_id.toString()
    this.props.threadSetter(str_m_id);
    history.pushState({}, "", "/" + this.props.currentChannel + "/" + str_m_id);
    this.props.get_replies_func(m_id);
  }

  render () {

    const messages = this.props.msg_arr.map((elem) =>
      <div key={elem.msg_id} id={"msg_id_" + elem.msg_id} className="chat_message">
        <div><b>{elem.display_name}</b></div>
        <div className="chat_body">{elem.body}</div>
        <div><button onClick={()=>this.showThread(elem.msg_id)}>Replies: {elem.num_replies}</button></div>
      </div>
    );

    if (this.props.isMobile && this.props.currentThread) {
      return null;
    }

    var cont_width = (this.props.isMobile) ? "95%" : this.props.width;

    return (
      <div className="current_channel" id="current_channel" style={{ width: cont_width }}>

        <div className="current_channel_name">
          <p id="current_channel_parag"><b>{this.props.currentChannel}</b></p>
        </div>

        <div className="current_channel_chat">
          <div className="current_channel_messages" id="current_channel_messages">
            {messages}
          </div>

          <div className="current_channel_comment_box">
            <input name="current_channel_comment" id="current_channel_comment_id"></input>
            <button onClick={()=>this.postMessage()}>Post</button>
          </div>
        </div>

      </div>
    );
  }
}

export default Chats;
