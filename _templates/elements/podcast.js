var transcript = {{ podcast.transcript|tojson }};

// 2. This code loads the IFrame Player API code asynchronously.
var tag = document.createElement('script');

tag.src = "https://www.youtube.com/iframe_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 3. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {
  player = new YT.Player('player', {
  //   height: '390',
  //   width: '640',
    videoId: '{{ podcast.YouTubeId }}',
    playerVars: {
      'playsinline': 1
    },
    events: {
      'onReady': onPlayerReady,
      // 'onStateChange': onPlayerStateChange
    }
  });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event) {
  console.log("Player ready");
  var sec = Number(location.href.split("#")[1]);
  if (sec){
    player.seekTo(sec, true);
  }
  player.playVideo();
  highlightParagraph();
}
function findParagraph(sec){
  var prev = transcript[0];
  for (var i = 0; i < transcript.length; i++) {
    var paragraph = transcript[i];
    if (sec >= paragraph.timestamp_s){
      prev = paragraph;
    } else {
      prev.end_s = paragraph.timestamp_s;
      prev.lenght_s = paragraph.timestamp_s - prev.timestamp_s;
      break
    }
  }
  return prev;
}
function seek(sec){
  if(player){
    player.playVideo();
    player.seekTo(sec, true);
  }
  console.log(findParagraph(sec));
}
var prevParagraph;
function highlightParagraph() {
  if (!player){
    return;
  }
  var currentTime = player.getCurrentTime();
  if (!currentTime){
    return;
  }
  var currentParagraph = findParagraph(currentTime);
  if (currentParagraph !== prevParagraph){
    prevParagraph = currentParagraph;
    Array.from(document.getElementsByClassName("transcript-paragraph")).forEach((e) => {
      e.classList.remove('text-white');
      e.classList.remove('bg-success');
    });
    var body = document.getElementById("body-"+currentParagraph.timestamp_s);
    body.classList.add('text-white');
    body.classList.add('bg-success');
    console.log(currentParagraph);
    var header = document.getElementById(""+currentParagraph.timestamp_s);
    header.scrollIntoView({behavior: "smooth"});
  }
}
time_update_interval = setInterval(highlightParagraph, 1000);
