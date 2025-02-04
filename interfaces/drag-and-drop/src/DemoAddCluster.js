import { Button, Card, Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useDrop } from 'react-dnd'
import { ItemTypes } from './Constants.js'

function DemoAddCluster({ addCluster, counter }) {
    const [{ isOver }, drop] = useDrop({
        accept: ItemTypes.IMAGE,
        canDrop: () => { return counter == 0 || counter == 2 || counter > 4; },
        drop: (image) => { addCluster(image.idx) },
        collect: (monitor) => ({
            isOver: monitor.isOver()
        }),
    });
    let bgColor = "#ffffff";
    if (isOver && (counter == 0 || counter == 2)) bgColor = "#cdffc8";
    if (isOver && counter != 0 && counter != 2 && counter <= 4) bgColor = "#ffc8c8";
    if (isOver && counter > 4) bgColor = "#f0f0f0";
    return (
        <Container>
            <Row className="w-100 align-items-center" ref={drop} style={{ minHeight: "200px", border: "2px dotted #d0d0d0", backgroundColor: bgColor }}>
                <Col style={{ color: "gray" }}>Add Group</Col>
            </Row>
        </Container>
    );
}

export default DemoAddCluster;
