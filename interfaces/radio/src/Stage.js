import Image from 'react-bootstrap/Image'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'

const Stage = ({ questions, questionNum }) => {
  return (
    <div id="stage" className='question-component' hidden>
      <Container>
        <Row key={'questionNum'}> <h3>Question {questionNum} / {process.env.REACT_APP_NUM_QUESTIONS}</h3></Row>
        <Row>
          <Col></Col>
          {
            questions.map((question, num) => {
              return (
                <Col key={question.imageId}>
                  <div>
                    <Image src={question.imageSrc} key={question.imageId} className='question-image' />
                    <p><b>Image {num + 1}</b></p>
                  </div>
                </Col>
              );
            })
          }
          <Col></Col>
        </Row>
      </Container>
    </div>
  );
}

export default Stage;