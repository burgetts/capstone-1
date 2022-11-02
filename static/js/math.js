const MINUTES = 5; // time on timer
let completed = 0; // math "score"


/* Get randomly generated math problem from Python API */
async function getProblem(){
    resp = await axios.get('/get-math')
    problem = resp.data.problem
    return problem + ' = ?'
}

/* Display math problem on page */
async function displayProblem(){
    p = await getProblem()
    $('.math-problem').html(p)
}

/* Update score on page */
function updateCompleted(){
    completed += 1
    $('#completed').html('Score: ' + completed)
}

/* Save math score */
function saveStats(){
    req = axios.post('/save-stats/math', {math_score: completed})
  }
  
  /* End game - remove timer and math forms, show button for next section.*/ 
function endGame(){
    // Remove form and timer
    $('#math-form').remove()
    $('#timer').remove()
    $('#skip-math').remove()
    $('#completed').remove()

    // append congrats messafge and form to math container
    $('#math-container').append(`<div class="instructions center"> Nice job! Your score for the math section is ${completed} </div>
                                 <form action="/reading/instructions"> <button type="submit" class="large-btn center"> Move on to reading </button> </form>`)
}

/* Control timer */
function manageTimer(){
    let minutes = MINUTES;
    let seconds = 00;

    timer = setInterval(() => {
        if (minutes === 0 && seconds < 1){
            clearInterval(timer)
            endGame()
            saveStats()
        }
        else if (seconds <= 10 && seconds >= 1){
            seconds= parseInt(seconds)
            seconds -= 1
            seconds = '0' + seconds
        }
        else if (seconds < 1){
            seconds = 59
            minutes -= 1
        }
        else {
            seconds -=1 
        }
    $('#timer').html('Time Left: ' + minutes + ':' + seconds)
    }, 1000)
}

/* Gameplay functions */ 
$(document).ready(function(){
    
    displayProblem()
    manageTimer()
    
    $('#math-form').on("submit", function(evt){
        evt.preventDefault()
        $('#math-answer').val('')
        updateCompleted()
        displayProblem()
    })

    $('#skip-math').on("submit", function(evt){
        evt.preventDefault()
        saveStats()
        endGame()
 
    })
})

