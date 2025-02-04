import { Button, Card , Col, Row, Image, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useDrop } from 'react-dnd'
import { ItemTypes } from './Constants.js'

function AddCluster({addCluster}){
    const [{isOver}, drop] = useDrop({
        accept: ItemTypes.IMAGE,
        drop: (image) => {addCluster(image.idx)},
        collect: (monitor) => ({
            isOver: monitor.isOver()
        }),
    });

    return (
        <Container>
            <Row className="w-100 align-items-center" ref={drop} style={{minHeight: "200px", border: "2px dotted #d0d0d0", backgroundColor: isOver ? "f0f0f0" : "#ffffff"}}>
                <Col style={{color: "gray"}}>Add Group</Col>
            </Row>
        </Container>
    );
}

export default AddCluster;
