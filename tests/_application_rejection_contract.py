"""Host input rejection must not masquerade as a C instruction frame."""
def assert_unexecuted_input_rejection(result):
 trace=result['execution_trace']
 assert result['success'] is False
 assert trace['success'] is False and trace['mutates'] is False
 assert trace['execution_started'] is False and trace['steps']==[]
 assert trace['final_state']==result['visual_state']
 assert trace['validation']['stage']=='API' and trace['validation']['accepted'] is False
 assert trace['validation']['message']==trace['message']==result['message']
