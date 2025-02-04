const Feedback = () => {
  return (
    <div id='feedback' className='question-component' hidden>
      <textarea
        id='feedback-textarea'
        rows={8}
        cols={64}
      />
    </div>
  );
}

export default Feedback;