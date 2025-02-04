import { Button, Card, Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useDrop } from 'react-dnd'
import { ItemTypes } from './Constants.js'

function DemoCluster({ title, idx, images, addImageToCluster, loadImages, removeCluster, validDropTarget, counter }) {
    const [{ isOver, canDrop }, drop] = useDrop({
        accept: ItemTypes.IMAGE,
        canDrop: (image) => validDropTarget(idx, image.idx),
        drop: (image) => { addImageToCluster(idx, image.idx) },
        collect: (monitor) => ({
            isOver: monitor.isOver(),
            canDrop: monitor.canDrop(),
        }),
    });
    let border = "";
    if (isOver && canDrop && counter <= 4) border = "success";
    if (isOver && !canDrop && counter <= 4) border = "danger";
    if (isOver && canDrop && counter > 4) border = "secondary";

    return (
        <Card className="w-100" border={border} ref={drop} style={{ minHeight: "200px" }}>
            <Card.Header>
                {renderTitle(title)}
            </Card.Header>
            <Card.Body>
                <Row><Col>{loadImages(images)}</Col></Row>
                <Row><Col>{idx === -1 ? <></> : <Button size="sm" variant="danger" disabled={(idx != 1 || counter != 3) && counter <= 4} onClick={() => removeCluster(idx)}>Remove Group</Button>}</Col></Row>
            </Card.Body>
        </Card>
    );
}

function renderTitle(title) {
    if (title === "Ungrouped") {
        return title;
    }
    return (<b>{title}</b>);
}


export default DemoCluster;
