import { useState } from 'react';
import get_dataset from './dataset';
import Instruction from './Instruction';
import Stage from './Stage';
import Submit from './Submit';
import Radios from './Radios';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Feedback from './Feedback';
import SurveyCode from './SurveyCode';

const dataset = get_dataset(process.env.REACT_APP_DATASET);
const sample = require('@stdlib/random-sample');
const _ = require('underscore')

function questionIterator() {
  let iterationCount = 0;
  const _questions = sample(_.range(dataset.length), {
    "size": process.env.REACT_APP_NUM_QUESTIONS * process.env.REACT_APP_NUM_IMAGES,
    "replace": false,
  });

  return {
    next: function () {
      if (iterationCount < process.env.REACT_APP_NUM_QUESTIONS) {
        iterationCount++;
        const numImages = process.env.REACT_APP_NUM_IMAGES;
        return { value: _questions.slice((iterationCount - 1) * numImages, iterationCount * numImages), done: false }
      } else {
        return { value: [], done: true }
      }
    }
  };
}
const questionIter = questionIterator();
let isDone = false;
let isInstructionPage = true;
let workerResults = [];

function App() {

  const [buttonName, setButtonName] = useState('Start');
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [time, setTime] = useState(Date.now());
  const [questionNum, setQuestionNum] = useState(0);
  const [isFeedback, setIsFeedback] = useState(false);
  const radioValues = JSON.parse(process.env.REACT_APP_RADIO_VALUES);

  /**
   * Recording data
   */
  const recordWorkerResult = () => {
    // calculate timeElapsed
    const timeElapsed = Date.now() - time;
    let answer = radioValues.map(radioValue => document.getElementById(radioValue)).filter(x => x.checked)[0];
    if (answer) {
      answer = answer.value;
    }
    const workerResult = {
      'questionNum': questionNum,
      'timeElapsed': timeElapsed,
      'originalOrder': questions,
      'clusters': answer
    };
    workerResults.push(workerResult);
  };

  /**
   * Setting UI
   */
  const postSubmission = () => {
    // uncheck all radio buttons
    radioValues.forEach(radioValue => {
      document.getElementById(radioValue).checked = false;
    });

    // reset time
    setTime(Date.now());

    // increment quesitonNum
    setQuestionNum(questionNum + 1);
  };

  const hideQuestion = () => {
    document.getElementById('stage').hidden = true;
    document.getElementById('radios').hidden = true;
  };

  const showQuestion = () => {
    document.getElementById('stage').hidden = false;
    document.getElementById('radios').hidden = false;
  };

  const jobsDone = () => {
    isDone = true;
    hideQuestion();
    setIsButtonDisabled(false);
    setIsFeedback(true);
    document.getElementById('feedback').hidden = false;
    setButtonName('Click here to get the survey code');
  };

  const recordWorkerFeedback = () => {
    const timeElapsed = Date.now() - time;
    workerResults.push({
      "timeElapsed": timeElapsed,
      "feedback": document.getElementById('feedback-textarea').value
    });
  };

  const submitWorkerResults = () => {
    const content = {
      'database': process.env.REACT_APP_EXPERIMENT_NAME,
      'demo': {},
      'result': workerResults,
      'practiceResult': {},
    };

    fetch('https://fakc7rsbwqw6cwc25sa72z3wy40amfzt.lambda-url.us-east-2.on.aws', {
      method: 'POST',
      headers: {
        "Content-Type": "text/plain",
      },
      body: JSON.stringify(content)
    })
      .then(res => res.json())
      .then(data => {
        document.getElementById('survey-code-loading').hidden = true
        document.getElementById('survey-code-content').hidden = false;
        document.getElementById('survey-code-value').innerHTML = data.insertedId;
      });
  };

  const handleSubmit = () => {
    if (isDone) {
      recordWorkerFeedback();
      // hide all question related ui
      const components = document.getElementsByClassName('question-component');
      Array.prototype.forEach.call(components, component => {
        component.hidden = true;
      })
      // show survey code component
      document.getElementById('survey-code').hidden = false;
      submitWorkerResults();
      return;
    }

    if (isInstructionPage) {
      showQuestion();
      setButtonName('Next');
      isInstructionPage = false;
    }

    // disable the button
    setIsButtonDisabled(true);

    // record worker responsd
    recordWorkerResult();

    const nextQuestion = questionIter.next();
    if (!nextQuestion.done) {
      setQuestions(nextQuestion.value.map(imageId => {
        return {
          imageId: imageId,
          imageSrc: dataset[imageId]
        };
      }));
    } else {
      jobsDone();
    }
    postSubmission();
  };

  return (
    <div className="App">
      <Container>
        <Row>
          <SurveyCode />
        </Row>
        <Row>
          <Instruction isFeedback={isFeedback} />
        </Row>
        <Row>
          <Stage questions={questions} questionNum={questionNum} />
        </Row>
        <Row>
          <Radios setIsButtonDisabled={setIsButtonDisabled} radioValues={radioValues} />
        </Row>
        <Row>
          <Feedback />
        </Row>
        <Row>
          <Submit buttonName={buttonName} handleSubmit={handleSubmit} isButtonDisabled={isButtonDisabled} />
        </Row>
      </Container>
    </div>
  );
}

export default App;
