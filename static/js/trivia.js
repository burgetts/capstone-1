
// Global variables
const BASE_URL = 'https://the-trivia-api.com/api/questions';
const NUM_QUESTIONS = 5;
//const DIFFICULTY = 'easy';
let questions = [];
let choices = [];
let question_num = 0;
let score = 0;

/* Fisher-Yates shuffle algorithm, shuffle in place */
function shuffle(arr) {
    let currentIndex = arr.length,  randomIndex;
  
    while (currentIndex != 0) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;
  
      [arr[currentIndex], arr[randomIndex]] = [
        arr[randomIndex], arr[currentIndex]];
    }
    return arr;
  }

  /* Get trivia choices for each question */
  function getChoices(question){ 
        // get answer choices and shuffle them
        choices = []
        choices.push(question.correctAnswer, ...question.incorrectAnswers)
        shuffle(choices)
        generateChoicesMarkup(question, choices)
  }

/* Get markup for trivia choices */
  function generateChoicesMarkup(question, choices){
        // Add input, label for each choice
        for (let choice of choices){

          // Generate + append li that wraps each individual choice
          $('.trivia-question').last().append('<li>')

          let $input_markup = $(`<input type="radio" name="choice${question_num}"></input>`)
          // if choice is correct, give it value of correct
          if (choice === question.correctAnswer){
            $input_markup.val('correct')
          } else {
              $input_markup.val('incorrect')
            }

          let $label_markup = `<label> ${choice} </label>`

          // Put radio button and label inside li
          $('li').last().append($input_markup)  
          $('li').last().append($label_markup) 
        }
  }

  /* Get trivia questions */
  async function getQuestions(){
    resp = await axios.get(BASE_URL, {params:{'limit': NUM_QUESTIONS}})
    questions = resp.data
    generateQuestionsMarkup(questions)
  }

 /* Generate markup for trivia questions */
  function generateQuestionsMarkup(questions){
    for (let question of questions){
        
        question_num += 1

        let $question = $('#trivia-container').append(`<ul class="trivia-question"> <span class="question"> ${question.question} </span></ul>`)
        let $result = $('.trivia-question').last().append('<span class=result> </span>')
        getChoices(question)
    }
  }

  /* Highlight correct answers in green */
  function highlightCorrectAnswers(){
    let $all_radio_buttons = $('input[type="radio"]')
    for (let button of $all_radio_buttons){
        // Show all correct answers in green
         if (button.value === 'correct'){
            $(button).next().addClass('correct li')
         }
        }
  }

/* Add correct or incorrect to end of trivia question */
  function addCorrectSpans(){
    let $all_questions = $('.trivia-question')
    for (let question of $all_questions){
        // Find checked value for each question
        let checked = $(question).find('input:checked')
        let result = $(question).find('.result')
        if (checked[0]){
            let input = checked[0]
            // Correct
            if (input.value === "correct"){
                score+=1
                result.html('<b> Correct </b>')
                result.addClass("correct")
            }
            // Incorrect
            else {
                result.html('<b> Incorrect </b>')
                result.addClass("incorrect")
            }
        }
        //  Mark incorrect if no answer
        else {
            result.html('<b> Incorrect </b>')
            result.addClass("incorrect")
        }
    }  
  }

 /* Prevent game from being played, direct to next exercise */
function endGame() {
        highlightCorrectAnswers()
        addCorrectSpans()

        $('#check-answers').remove()
        $('#trivia-container').append('<form action="/math/instructions"><button class="math-button large-btn center"> On to math! </button> </form>')
        $('input[type="radio"]').attr('disabled', true)
}

/* Save trivia score */
function saveStats(){
    score = score + `/${NUM_QUESTIONS}`
    req = axios.post('/save-stats/trivia', {trivia_score: score})
}

/* Gameplay functions */
$(document).ready(function() {
    getQuestions()

    $('#check-answers').submit(function(evt){
        evt.preventDefault()
        endGame()
        saveStats()
        }
    )
})

