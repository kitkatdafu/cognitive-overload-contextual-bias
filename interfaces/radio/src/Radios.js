import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

const Radios = ({ setIsButtonDisabled, radioValues, questionNum }) => {
  return (
    <div id="radios" className='question-component' hidden>
      <Container>
        {
          radioValues.map((radioValue) => {
            return (
              <Row key={radioValue}>
                <label><input name="radios" type="radio" value={radioValue} onClick={() => setIsButtonDisabled(false)} key={radioValue} id={radioValue} /> {radioValue} </label>
              </Row>
            );
          })
        }
      </Container>
    </div>
  );
}

export default Radios;