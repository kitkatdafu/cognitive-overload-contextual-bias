import React, { useState } from 'react'
import { Button, Card, Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import Cluster from './Cluster.js'
import AddCluster from './AddCluster.js'
import useMousePosition from './useMousePosition.js'

function Question({ number, images, loadImages, submit, numQuestions }) {

    const groupName = document.querySelector("#group-name").innerText.trim();
    const imageType = document.querySelector("#image-type").innerText.trim();
    const [clusters, setClusters] = useState([]);
    const [ungrouped, setUngrouped] = useState(images);
    const [errorState, setError] = useState(false);
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
        setHistory([...clusterHistory, newClusters])
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
                    clusterArr.push(<Col><Cluster title={"Breed " + (j + 1)} idx={j} images={clusters[j]} addImageToCluster={addImageToCluster} loadImages={loadImages} removeCluster={removeCluster} validDropTarget={validDropTarget} /></Col>);
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

    function next() {
        if (ungrouped.length > 0) {
            setError(true);
            return;
        }
        setError(false);
        let submissionInfo = {
            questionNum: number + 1,
            clusters: clusters,
            originalOrder: images,
            clusterHistory: clusterHistory,
        };
        submit(submissionInfo);
    }

    return (
        <Container style={{ textAlign: "center" }}>
            <Row className="mt-2">
                <Card className="w-100">
                    <Card.Header>Question {number + 1}/{numQuestions}</Card.Header>
                    <Card.Body>
                        <p>Please carefully group the {imageType} according to their breed <b><em>(same breed in the same group, different {groupName} in different groups)</em></b>.</p>
                        <p style={{ display: errorState ? "block" : "none", color: "red" }}>Please move all the images into clusters before continuing.</p>
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
}

export default Question;
