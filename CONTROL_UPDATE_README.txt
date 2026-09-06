WattWise Control Recommendation Update

Replace the files in this archive over your existing project, preserving the paths.

Added:
- ml/control_action_classifier.py
- ml/control_dataset_generator.py
- ml/train_control.py
- ml/models/control_action_classifier.joblib
- data/control_training_dataset.json
- recommendations/control_engine.py
- tests/test_control_recommendations.py

Replaced:
- app/intelligence.py

Verification:
- Control dataset: 420 samples (60 per EMS action)
- Control model: RandomForestClassifier, 300 trees
- Validation accuracy: 1.0000
- Test accuracy: 1.0000
- Full test suite: 207 passed

Important:
- Existing intelligence_output.recommendation field is unchanged.
- No new public control_action field is added.
- Control actions are condition-gated by telemetry.
- Maintenance/safety findings are not converted into EMS control actions.
