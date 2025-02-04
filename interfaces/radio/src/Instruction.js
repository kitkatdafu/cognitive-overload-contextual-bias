const Instruction = ({ isFeedback }) => {
  if (!isFeedback) {
    return (
      <div id="instruction" className='question-component'>
        <h1>Instructions:</h1>
        <ul>
          <li>Thank you for your interest!</li>
          <li>You will be shown {process.env.REACT_APP_NUM_QUESTIONS} {process.env.REACT_APP_QUESTION_UNIT} of images with {process.env.REACT_APP_IMAGE_TYPE} in them.</li>
          <li>For each question, you will see {process.env.REACT_APP_NUM_RADIO_BUTTONS} radio buttons.&nbsp;</li>
          <li>For the {process.env.REACT_APP_NUM_IMAGES} images shown to you,</li>
          <ul>
            {
              JSON.parse(process.env.REACT_APP_INSTR).map(instr => {
                const then_click_on = " then click on ";
                const preciate = instr.split(then_click_on)[0];
                const button_name = instr.split(then_click_on)[1];
                return (<li key={instr}>{preciate + then_click_on}<code>{button_name}</code></li>);
              })
            }
          </ul>
          <li>You need to answer all the questions.</li>
          <li>Of the {process.env.REACT_APP_NUM_QUESTIONS}, there are {process.env.REACT_APP_NUM_GOLDEN_QUESTIONS} (random out of {process.env.REACT_APP_NUM_QUESTIONS}) GOLD STANDARD questions. You need to get at least {process.env.REACT_APP_NUM_CORRECT_GOLDEN_QUESTIONS} of them correct to get the answers accepted.</li>
        </ul>
      </div>
    );
  } else {
    return (
      <div id="instruction" className='question-component'>
        <h1>Instructions:</h1>
        <p>Thanks for participating! If you have any feedback, feel freee to leave a note below.</p>
        <p>You need to <b>click</b> the button below to submit your result and to retrieve the survey code.</p>
      </div>
    )
  }
}

export default Instruction;