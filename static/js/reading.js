BASE_URL = 'https://shortstories-api.onrender.com/'

/* Handle story UI */
function displayStory(story, title, author){
    $('#story-title').html('<b>' + title + '</b>' )
    $('#story-author').html('By: ' + author)
    $('#story').html(story)
}

/* Get story info from API */
async function getStory(){
    let resp = await axios.get(BASE_URL)
    let story = resp.data.story
    let title = resp.data.title
    let author = resp.data.author
    displayStory(story, title, author)
}

$(document).ready(function(){
    getStory()
})

