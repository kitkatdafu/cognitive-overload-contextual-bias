import Button from 'react-bootstrap/Button';

const Submit = ({ buttonName, handleSubmit, isButtonDisabled }) => {
  return (
    <div className='question-component' id="submit">
      <Button variant="primary" size="lg" onClick={handleSubmit} disabled={isButtonDisabled}>
        {buttonName}
      </Button>
    </div>
  );
}

export default Submit;