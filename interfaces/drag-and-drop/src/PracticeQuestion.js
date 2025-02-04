import React, { useState } from 'react'
import { Button, Card, Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import Cluster from './Cluster.js'
import AddCluster from './AddCluster.js'
import useMousePosition from './useMousePosition.js'
const _ = require('underscore')

const PracticeQuestion = ({ number, images, correct, submit, loadImages, numImages }) => {

    const groupName = document.querySelector("#group-name").innerText.trim();
    const imageType = document.querySelector("#image-type").innerText.trim();
    const [clusters, setClusters] = useState([]);
    const [ungrouped, setUngrouped] = useState(images);
    const [isCorrect, setIsCorrect] = useState(true);
    const [numAttempts, setNumAttempts] = useState(0);
    const [clusterHistory, setHistory] = useState([[]]);

    const addImageToCluster = (clusterIdx, imageIdx) => {
        let newClusters = [];
        clusters.forEach((cluster) => {
            newClusters.push(cluster.filter(img => img != imageIdx));
        });
        setUngrouped(ungrouped => ungrouped.filter(img => img != imageIdx));
        if (clusterIdx === -1) {
            setUngrouped(ungrouped => [...ungrouped, imageIdx]);
        }
        else if (clusterIdx === newClusters.length) {
            newClusters.push([]);
            newClusters[clusterIdx].push(imageIdx);
        }
        else {
            newClusters[clusterIdx].push(imageIdx);
        }
        let iter = 0;
        while (iter < newClusters.length) {
            if (newClusters[iter].length == 0) {
                newClusters.splice(iter, 1);
                continue;
            }
            iter++;
        }
        setClusters(newClusters);
        setHistory([...clusterHistory, newClusters]);
    }




    function loadClusters() {
        let ret = [];
        let numClusters = (clusters.length == images.length) ? clusters.length : clusters.length + 1;
        for (let i = 0; i <= Math.floor(numClusters / 3); i++) {
            let clusterArr = [];
            for (let j = i * 3; j < numClusters && j < (i + 1) * 3; j++) {
                if (j == clusters.length) {
                    clusterArr.unshift(<Col><AddCluster addCluster={addCluster} /></Col>);
                }
                else {
                    clusterArr.push(<Col><Cluster title={"Group " + (j + 1)} idx={j} images={clusters[j]} addImageToCluster={addImageToCluster} loadImages={loadImages} removeCluster={removeCluster} validDropTarget={validDropTarget} /></Col>);
                }
            }
            ret.push(
                <Row className="w-90 mt-2">{clusterArr}</Row>
            );
        }
        return ret;
    }

    const addCluster = (image) => {
        if (image != undefined && image != null) {
            addImageToCluster(clusters.length, image);
        }
        else {
            setClusters(clusters => [...clusters, []]);
        }
    }

    const removeCluster = (clusterIdx) => {
        let removed = clusters[clusterIdx];
        setClusters(clusters => clusters.filter((cur, idx) => { if (idx != clusterIdx) return cur; }));
        removed.forEach((element) => {
            setUngrouped(ungrouped => [...ungrouped, element]);
        });
    }

    const validDropTarget = (clusterIdx, imageIdx) => {
        let origCluster = -1;
        clusters.forEach((cluster, idx) => {
            if (cluster.includes(imageIdx)) {
                origCluster = idx;
            }
        });
        return clusterIdx !== origCluster;
    }

    function eqSet(as, bs) {
        if (as.size !== bs.size) return false;
        for (var a of as) if (!bs.has(a)) return false;
        return true;
    }

    function checkCorrectness() {
        const clusterSet = new Set(correct);
        const true_clustering = [];

        // if no clusters, return false
        if (clusters.length == 0) {
            return false;
        }

        // if the number of clustered items is not equals to the total number of items, return false
        if (clusters.map(cluster => cluster.length).reduce((x, y) => x + y) !== correct.length) {
            return false;
        }

        for (var i = 0; i < clusterSet.size; i++) {
            true_clustering.push([]);
        }
        for (var i = 0; i < correct.length; i++) {
            const cluster_id = correct[i];
            true_clustering[cluster_id].push(images[i]);
        }

        // if the true number of clusters is not equal to the worker's number of clusters, return false
        if (true_clustering.length !== clusters.length) {
            // return false;
        }

        let _isCorrect = true;
        clusters.forEach(predicted_cluster => {
            let matched = false;
            true_clustering.forEach(true_cluster => {
                matched = matched || eqSet(new Set(predicted_cluster), new Set(true_cluster));
            });
            // make sure _isCorrect cannot be set back to True
            if (_isCorrect) {
                _isCorrect = matched;
            }
        })

        return _isCorrect;
    }

    function next() {
        let correctness = true;
        let submissionInfo = {
            questionNum: number,
            clusters: clusters,
            originalOrder: images,
            clusterHistory: clusterHistory,
            attemptNum: numAttempts + 1,
        };

        const _isCorrect = checkCorrectness();
        if (!_isCorrect) {
            setNumAttempts(numAttempts + 1);
        }

        correctness = _isCorrect;

        if (numAttempts === 2 || correctness) {
            setIsCorrect(true);
            submit(submissionInfo, correctness, true);
        } else {
            setIsCorrect(false);
            submit(submissionInfo, correctness, false);
        }
    }

    return (
        <Container style={{ textAlign: "center" }}>

            <Row className="mt-2">
                <Card className="w-100">
                    <Card.Header>Practice {number}/3</Card.Header>
                    <Card.Body>
                        <p>Please group the {imageType} according to their breed <b><em>(same breed in the same group, different breeds in different groups)</em></b>.</p>
                        {!isCorrect &&
                            <p style={{ color: "red" }}>
                                Your answer is not correct, please try again (attempt {numAttempts}/3).
                                Please pay attention to correctly group the dogs according to their breed <b><em>(same breed in the same group, different breeds in different groups)</em></b>.
                            </p>
                        }
                    </Card.Body>
                </Card>
            </Row>

            <Row className="mt-2">
                <Cluster title="Ungrouped" idx={-1} images={ungrouped} addImageToCluster={addImageToCluster} loadImages={loadImages} removeCluster={removeCluster} validDropTarget={validDropTarget} />
            </Row>
            <Row>
                <Card className="mt-1 w-100">
                    <Card.Header>
                        <Row>
                            <Col>Groups</Col>
                        </Row>
                    </Card.Header>
                    <Card.Body>
                        {loadClusters()}
                    </Card.Body>
                </Card>
            </Row>
            <Row>
                <Col md={{ span: 1, offset: 11 }}>
                    <Button variant="dark" size="sm" className="m-2" onClick={() => next()}>Submit</Button>
                </Col>
            </Row>
        </Container>
    );
};

export default PracticeQuestion;
