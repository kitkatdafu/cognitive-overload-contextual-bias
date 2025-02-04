import ReactLoading from 'react-loading';

const SurveyCode = () => {
  return (
    <div className='survey-code-component' id='survey-code' hidden>
      <div id='survey-code-loading'>
        <h1>Retrieving survey code...</h1>
        <ReactLoading color="#000000" height={'20%'} width={'20%'} />
      </div>
      <div id='survey-code-content' hidden>
        <h1>Your <em>survey code</em> is <code id='survey-code-value'></code></h1>
        <h2>Please copy and paste this code back to mturk.</h2>
      </div>
    </div>
  );
}

export default SurveyCode;