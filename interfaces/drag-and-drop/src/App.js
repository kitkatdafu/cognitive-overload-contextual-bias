import random from 'random';
import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Container, Form, Row } from 'react-bootstrap';
import { isIE, isMobile } from 'react-device-detect';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import ReactLoading from 'react-loading';
import _ from 'underscore';
import Demo from './Demo.js';
import DraggableImage from './DraggableImage.js';
import PracticeQuestion from './PracticeQuestion.js';
import Question from './Question.js';
import useMousePosition from './useMousePosition.js';
const seedrandom = require('seedrandom');

const imageType = document.querySelector("#image-type").innerText.trim();
const imageTypeSingular = document.querySelector("#image-type-singular").innerText.trim();
const groupName = document.querySelector("#group-name").innerText.trim();
const groupNameSingular = document.querySelector("#group-name-singular").innerText.trim();
const numGolden = parseInt(document.querySelector("#num-golden").innerText.trim());
const numAtLeastGolden = parseInt(document.querySelector("#num-at-least-golden").innerText.trim());
const instr_detailed_list = JSON.parse(process.env.REACT_APP_INSTR_DETAILED_LIST);

const images = JSON.parse(document.querySelector("#images").innerText.trim());
const practiceImages = JSON.parse(document.querySelector("#demo-images").innerText.trim());
const numQuestions = parseInt(document.querySelector("#num-questions").innerText.trim());
const numImages = parseInt(document.querySelector("#num-images").innerText.trim());
const questions = genImages(numImages, numQuestions);
const database = document.querySelector("#database").innerText.trim();
const [practiceQuestions, practiceCorrects] = genPracticeImages(numImages);
var mouseHistory = [[0, 0]];
var mouseUpdateInterval = parseInt(document.querySelector("#mouse-interval").innerText.trim());

function genPracticeImages(numImages) {
    let questions = [];
    let corrects = [];
    let indices = [0, 14, 18];

    questions.push(_.range(numImages));
    corrects.push(Array(numImages).fill(0));

    let question = _.last(indices, 2);
    let correct = _.range(2);
    question = question.concat(_.range(numImages, 2 * numImages - 2));
    correct = correct.concat(Array(numImages - 2).fill(Math.min(2)));


    questions.push(question);
    corrects.push(correct);

    question = _.last(indices, 2).map(i => i + 1);
    correct = _.range(2);
    question = question.concat(_.range(2 * numImages - 2, 2 * numImages - 2 + numImages - 2));
    correct = correct.concat(Array(numImages - 2).fill(Math.min(2)));

    questions.push(question);
    corrects.push(correct);

    return [questions, corrects];
}

function genImages(numImages, numQuestions) {
    let questions = [];
    let used = new Set();
    for (var i = 0; i < numQuestions; i++) {
        let preset = document.querySelector("#question" + (i + 1));
        let cur = [];
        if (preset !== null) {
            cur = JSON.parse(preset.innerText.trim());
        }
        else {
            for (var j = 0; j < numImages; j++) {
                let k = Math.floor(random.float() * images.length);
                while (used.has(k)) {
                    k = Math.floor(random.float() * images.length);
                }
                used.add(k);
                cur.push(k);
            }
        }
        questions.push(cur);
    }
    return questions;
}

function App() {
    const [counter, setCounter] = useState(-7);
    const [submission, setSubmission] = useState([]);
    const [practiceSubmission, setPracticeSubmission] = useState([]);
    const [time, setTime] = useState(Date.now());
    const [feedback, setFeedback] = useState("");
    const { x, y } = useMousePosition();
    const hasMovedCursor = typeof x === "number" && typeof y === "number";
    const [demoTimes, setDemoTimes] = useState([]);
    const [demoStepTimes, setDemoStepTimes] = useState([]);
    const [demoIncorrectTimes, setDemoIncorrect] = useState(0);
    if (Date.now() - time > mouseUpdateInterval * mouseHistory.length) {
        if (!hasMovedCursor) {
            mouseHistory.push(mouseHistory[mouseHistory.length - 1]);
        }
        else {
            mouseHistory.push([x, y]);
        }
    }

    const practiceSubmit = (submissionInfo, correctness, isLastAttempt) => {
        submissionInfo["timeElapsed"] = Date.now() - time;
        submissionInfo["mouseHistory"] = JSON.parse(JSON.stringify(mouseHistory));
        submissionInfo["mouseUpdateInterval"] = mouseUpdateInterval;
        submissionInfo["correctness"] = correctness;
        mouseHistory = [[0, 0]];
        setPracticeSubmission([...practiceSubmission, submissionInfo]);
        setTime(Date.now());
        if (isLastAttempt || correctness) {
            setCounter(counter + 1);
        }
    };

    const submit = (submissionInfo) => {
        submissionInfo["timeElapsed"] = Date.now() - time;
        submissionInfo["mouseHistory"] = JSON.parse(JSON.stringify(mouseHistory));
        submissionInfo["mouseUpdateInterval"] = mouseUpdateInterval;
        mouseHistory = [[0, 0]];
        setSubmission([...submission, submissionInfo]);
        setCounter(counter + 1);
        setTime(Date.now());
    };

    const next = () => {
        if (counter === numQuestions) {
            setSubmission([...submission, { "feedback": feedback }]);
        }
        setTime(Date.now());
        setCounter(counter + 1);
    }

    const loadImages = (indices) => {
        return indices.map((idx) => { return <DraggableImage className="m-2" idx={idx} src={images[idx]} style={{ maxWidth: "300px", maxHeight: "300px" }} /> })
    }

    const loadPracticeImages = (indices) => {
        return indices.map((idx) => { return <DraggableImage className="m-2" idx={idx} src={practiceImages[idx]} style={{ maxWidth: "300px", maxHeight: "300px" }} /> })
    }

    const completeDemo = (stepTimes, demoIncorrect) => {
        setDemoIncorrect(demoIncorrect);
        setCounter(counter + 1);
        setDemoStepTimes(stepTimes);
        setDemoTimes([...demoTimes, Date.now() - time]);
        setTime(Date.now());
    }

    useEffect(() => {
        if (counter === numQuestions + 1) {
            // un comment the following lines if HIT is created using terminal
            // const queryStr = window.location.search;
            // const searchParams = new URLSearchParams(queryStr);
            // const assignmentId = searchParams.get('assignmentId');
            // const turkSubmitTo = searchParams.get('turkSubmitTo');
            // const postUrl = turkSubmitTo + "?result=" + result + "&assignmentId=" + assignmentId + "&practiceResult=" + practiceResult;
            // window.location.replace(postUrl);

            const result = document.querySelector('pre').innerHTML;
            const practiceResult = document.querySelector('#practice-submission').innerHTML;
            const demoTimes = JSON.parse(document.querySelector('#demo').innerHTML);
            demoStepTimes[0] -= demoTimes[0];
            const demoObj = {
                "beforeDemoTime": demoTimes[0],
                "demoCompletionTime": demoTimes[1],
                "betweenDemoPracticeTime": demoTimes[2],
                "betweenPracticeActualQuestionTime": demoTimes[3],
                "demoStepTimes": demoStepTimes,
                "demoIncorrectTimes": demoIncorrectTimes
            };

            const content = {
                database: database,
                result: JSON.parse(result),
                practiceResult: JSON.parse(practiceResult),
                demo: demoObj
            };

            document.querySelector('.loading').hidden = false;
            fetch('https://fakc7rsbwqw6cwc25sa72z3wy40amfzt.lambda-url.us-east-2.on.aws', {
                method: 'POST',
                headers: {
                    "Content-Type": "text/plain",
                },
                body: JSON.stringify(content)
            })
                .then(res => res.json())
                .then(data => {
                    document.querySelector('.loading').hidden = true;
                    document.querySelector('.survey-code-message').hidden = false;
                    document.querySelector('.survey-code-value').innerHTML = data.insertedId;
                });
        }
    }, [submission]);


    function loadQuestions() {
        let questionList = [];
        questionList.push(<div style={{ display: (counter === -6) ? "block" : "none" }}><Demo completeDemo={completeDemo} numImages={numImages} /></div>);
        for (var i = -4; i < -1; i++) {
            questionList.push(<div style={{ display: (counter === i) ? "block" : "none" }}><PracticeQuestion number={i + 5} images={practiceQuestions[i + 4]} loadImages={loadPracticeImages} submit={practiceSubmit} correct={practiceCorrects[i + 4]} numImages={numImages} /></div>);
        }
        for (var i = 0; i < numQuestions; i++) {
            questionList.push(<div style={{ display: (counter === i) ? "block" : "none" }}><Question number={i} images={questions[i]} loadImages={loadImages} submit={submit} numQuestions={numQuestions} /></div>);
        }
        return questionList;
    }

    function loadMessage() {
        if (counter === -7) {
            return (
                <div className='instruction'>
                    <p>Thank you for your interest!</p>
                    <ul>
                        <li>This task involves <em><b>grouping images of {imageType} according to their {groupNameSingular}.</b></em></li>
                        <li>You will be asked {numQuestions} questions. Each question has {numImages} images of {imageType}.</li>
                        <li>Your task for each question is to group the {imageType} according to their breeds by comparing the images shown.</li>
                    </ul>
                    <ul>
                        <li>For the {numImages} images shown to you, it is possible, but not limited to, that</li>
                        <ul>
                            {
                                instr_detailed_list.map((item) => {
                                    return (<li>{item}</li>);
                                })
                            }
                        </ul>
                    </ul>
                    <ul>
                        <li>Please observe the images carefully as you group them since accurate answers would be helpful for our study.</li>
                        <li>Please avoid any distractions during the task.</li>
                        <li>Click <code>Start Demo</code> to learn how to use our interface to group the {imageType}.</li>
                    </ul>
                </div>
            );
        } else if (counter === -5) {
            return "Now that you have completed the demo, let's do some practices. Click the button below to practice.";
        } else if (counter === -1) {
            return (
                <div className='instruction'>
                    <ul>
                        <li>You will be shown {numQuestions} questions. Each question has {numImages} images of {imageType}.</li>
                        <li>Please group the {imageType} according to their breed <b><em>(same breed in the same group, different breeds in different groups)</em></b></li>
                        <li>Please observe the images carefully as you group them since accurate answers would be helpful for our study.</li>
                        <li>Please note that you will only have 1 attempt for each question from now on.</li>
                        <li hidden={process.env.REACT_APP_GOLDEN_STANDARD_MSG == 0}>
                            <ul>
                                <li>Of the {numQuestions} questions, there are {numGolden} (random out of {numQuestions}) GOLD STANDARD questions.</li>
                                <li>You need to get at least {numAtLeastGolden} of them correct to receive credit.</li>
                            </ul>
                        </li>
                        <li>Click the <code>Continue</code> button below when you are ready.</li>
                    </ul>
                </div>
            )
        }
    }

    if (isMobile) {
        return <h1>Thank you for your interest. This task needs a larger screen, and hence available only on desktop/laptops.</h1>;
    } else if (isIE) {
        return <h1>Thank you for your interest. The task is incompatible with IE. Please use a different browser.</h1>;
    } else {
        return (
            < DndProvider backend={HTML5Backend} >
                <Container style={{ textAlign: "center" }}>
                    <div style={{ display: (counter === -7 || counter === -5 || counter == -1) ? "block" : "none" }}>
                        <Row className="mt-2">
                            <Card className="w-100">
                                <Card.Header>Instructions </Card.Header>
                                <Card.Body>
                                    {loadMessage()}
                                </Card.Body>
                            </Card>
                        </Row>
                        <Row className="mt-2">
                            <Col><Button variant="dark" size="sm" className="m-2" onClick={() => { setCounter(counter + 1); setDemoTimes([...demoTimes, Date.now() - time]); setTime(Date.now()); }}>{counter === -7 ? "Start Demo" : "Continue"}</Button></Col>
                        </Row>
                    </div>
                    {loadQuestions()}
                    <div style={{ display: counter === numQuestions ? "block" : "none" }}>
                        <Row className="mt-2">
                            <Card className="w-100">
                                <Card.Header>Feedback</Card.Header>
                                <Card.Body>
                                    <p>Thanks for participating! If you have any feedback, feel free to leave a note below! You need to <b>click</b> the button below to submit your result and to retrieve the survey code.</p>
                                    <Form>
                                        <Form.Group controlId="feedbackForm">
                                            <Form.Control as="textarea" rows={5} onChange={(e) => setFeedback(e.target.value)} />
                                        </Form.Group>
                                    </Form>
                                </Card.Body>
                            </Card>
                        </Row>
                        <Row className="mt-2">
                            <Col><Button variant="dark" size="lg" className="m-2" onClick={() => next()}>{counter === -7 ? "Start Demo" : (counter === numQuestions ? "Click here to get the survey code" : "Continue")}</Button></Col>
                        </Row>
                    </div>
                    <div>
                        <div hidden className='loading'>
                            <h1>Retrieving survey code...</h1>
                            <center>
                                <ReactLoading color="#000000" height={'10%'} width={'10%'} />
                            </center>
                        </div>
                        <div hidden className='survey-code-message'>
                            <h1>Your Survey Code is: <code className='survey-code-value'>123123</code></h1>
                            <h2>Please copy and paste this code back to mturk.</h2>
                        </div>
                    </div>
                    <pre hidden> {JSON.stringify(submission)} </pre>
                    <div hidden id="practice-submission"> {JSON.stringify(practiceSubmission)} </div>
                    <div hidden id="demo"> {JSON.stringify(demoTimes)} </div>
                    <div hidden id="demo-step-times">{JSON.stringify(demoStepTimes)}</div>
                </Container>
            </DndProvider >
        );
    }
}

export default App;
