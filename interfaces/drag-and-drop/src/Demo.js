import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import DemoCluster from './DemoCluster.js';
import DemoAddCluster from './DemoAddCluster.js';
import DraggableImage from './DraggableImage.js';
const _ = require('underscore');

function Demo({ completeDemo, numImages }) {
    const inp_images = JSON.parse(document.querySelector("#demo-images").innerText.trim());
    const inp_correct = JSON.parse(document.querySelector("#demo-clusters").innerText.trim());
    const imageType = document.querySelector("#image-type").innerText.trim();
    const imageTypeSingular = document.querySelector("#image-type-singular").innerText.trim();

    numImages = Math.min(numImages, inp_images.length);

    const unique = new Set();
    const images = [];
    const correct = [];

    inp_images.forEach((image, i) => {
        images.push(image);
        correct.push(inp_correct[i]);
        unique.add(inp_correct[i]);
    });

    const firstGroupNum = Math.floor(numImages / 2);
    const secondGroupNum = numImages - firstGroupNum;
    const originalOrder = _.range(firstGroupNum).concat(_.range(14, 14 + secondGroupNum));

    const [counter, setCounter] = useState(0);
    const [demoIncorrect, setDemoIncorrect] = useState(0);
    const [clusters, setClusters] = useState([]);
    const [ungrouped, setUngrouped] = useState(_.range(firstGroupNum).concat(_.range(14, 14 + secondGroupNum)));
    const [errorMsg, setErrorMsg] = useState("");
    const [errorState, setError] = useState(false);
    const [times, setTimes] = useState([]);
    const [time, setTime] = useState(Date.now());

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
                if (counter == 4) {
                    setTimes([...times, Date.now() - time]);
                    setTime(Date.now());
                    setCounter(counter + 1);
                }
                continue;
            }
            iter++;
        }
        setClusters(newClusters);
        if (counter == 1 || counter == 3) {
            setTimes([...times, Date.now() - time]);
            setTime(Date.now());
            setCounter(counter + 1);
        }
    }

    const loadImages = (indices) => {
        return indices.map((idx) => { return <DraggableImage className="m-2" key={idx} idx={idx} src={images[idx]} style={{ maxWidth: "200px", maxHeight: "200px" }} /> })
    }

    function loadClusters() {
        let ret = [];
        let numClusters = (clusters.length == images.length) ? clusters.length : clusters.length + 1;
        for (let i = 0; i <= Math.floor(numClusters / 3); i++) {
            let clusterArr = [];
            for (let j = i * 3; j < numClusters && j < (i + 1) * 3; j++) {
                if (j == clusters.length) {
                    clusterArr.unshift(<Col><DemoAddCluster addCluster={addCluster} counter={counter} /></Col>);
                }
                else {
                    clusterArr.push(<Col><DemoCluster title={"Breed " + (j + 1)} idx={j} images={clusters[j]} addImageToCluster={addImageToCluster} loadImages={loadImages} removeCluster={removeCluster} validDropTarget={validDropTarget} counter={counter} /></Col>);
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
        if (counter == 0 || counter == 2) {
            setTimes([...times, Date.now() - time]);
            setTime(Date.now());
            setCounter(counter + 1);
        }
    }

    const removeCluster = (clusterIdx) => {
        let removed = clusters[clusterIdx];
        setClusters(clusters => clusters.filter((cur, idx) => { if (idx != clusterIdx) return cur; }));
        removed.forEach((element) => {
            setUngrouped(ungrouped => [...ungrouped, element]);
        });
        if (counter == 3) {
            setTimes([...times, Date.now() - time]);
            setTime(Date.now());
            setCounter(counter + 1);
        }
    }

    function submit() {
        if (ungrouped.length > 0) {
            setError(true);
            setErrorMsg("Please try again. Please carefully group the dogs according to their breed");
            setDemoIncorrect(demoIncorrect + 1);
            return;
        }

        let flag = false;
        // we are certain that there is should only be 2 groups
        if (clusters.length != 2) {
            flag = true;
        }
        clusters.forEach(cluster => {
            // cluster_id_set should have a length of 1 only
            const cluster_id_set = new Set(cluster.map(image_index => correct[image_index]));
            if (cluster_id_set.size != 1) {
                flag = true;
            }
        });

        if (flag) {
            setError(true);
            setErrorMsg("Please try again. Please carefully group the dogs according to their breed");
            setDemoIncorrect(demoIncorrect + 1);
            return;
        }
        setError(false);
        completeDemo(times, demoIncorrect);
    }

    function displayInstructions() {
        switch (counter) {
            case 0:
                return (<p>Welcome. In this demonstration, you can create a new group by dragging a {imageTypeSingular} onto the <em>Add Group</em> area. Try to drag a {imageTypeSingular} onto the <em>Add Group</em> area. The mouse pointer should enter the group you are dragging the image to.</p>);
            case 1:
                return (<p>Good job. Drag another {imageTypeSingular} to the first group. The mouse pointer should enter the group you are dragging the image to.</p>)
            case 2:
                return (<p>You can create a new group by dragging a {imageTypeSingular} onto the <em>Add Group</em> area. Place a {imageTypeSingular} into a new group. The mouse pointer should enter the group you are dragging the image to.</p>)
            case 3:
                return (<p>Great! You can remove a group by clicking the <em>Remove Group</em> button and the {imageType} will return to the ungrouped section. Try removing the second group.</p>)
            case 4:
                return (<p>Removing all {imageType} from a group also remove that group. Try dragging all the {imageType} out of the last group.</p>)
            case 5:
                return (<p>Now, please group the {imageType} according to their breed <b><em>(same breed in the same group, different breeds in different groups)</em></b>.</p>)
        }
    }

    const validDropTarget = (clusterIdx, imageIdx) => {
        let origCluster = -1;
        clusters.forEach((cluster, idx) => {
            if (cluster.includes(imageIdx)) {
                origCluster = idx;
            }
        });
        switch (counter) {
            case 0:
                return false;
            case 1:
                return clusterIdx == 0 && clusterIdx !== origCluster;
            case 2:
                return false;
            case 3:
                return false;
            case 4:
                return clusterIdx == -1 && clusterIdx !== origCluster;
        }
        return clusterIdx !== origCluster;
    }

    return (
        <Container style={{ textAlign: "center" }}>

            <Row className="mt-2">
                <Card className="w-100">
                    <Card.Header>Instructions</Card.Header>
                    <Card.Body>
                        {displayInstructions()}
                        <p style={{ display: errorState ? "block" : "none", color: "red" }}>{errorMsg}<b><em> (same breed in the same group, different breeds in different groups).</em></b></p>
                    </Card.Body>
                </Card>
            </Row>

            <Row className="mt-2">
                <DemoCluster title="Ungrouped" idx={-1} images={ungrouped} addImageToCluster={addImageToCluster} loadImages={loadImages} validDropTarget={validDropTarget} counter={counter} />
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
                    <Button variant="dark" size="sm" className="m-2" disabled={counter <= 4} onClick={() => submit()}>Submit</Button>
                </Col>
            </Row>
        </Container>
    );
}

export default Demo;
