import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

print("=" * 60)
print("IMPROVED NEURAL NETWORK - ANTI-OVERFITTING")
print("=" * 60)

# Path for exported data
DATA_PATH = os.path.join('MP_Data')

# Automatically detect actions from the MP_Data directory
if os.path.exists(DATA_PATH):
    actions = np.array(sorted([folder for folder in os.listdir(DATA_PATH)
                               if os.path.isdir(os.path.join(DATA_PATH, folder))]))
else:
    print(f"❌ Error: {DATA_PATH} directory not found!")
    print("   Please run CollectData.py first to collect training data.")
    exit()

print(f"\n✅ Detected actions: {actions}")
print(f"✅ Number of actions: {len(actions)}")

# Detect number of sequences from first action
first_action_path = os.path.join(DATA_PATH, actions[0])
no_sequences = len([seq for seq in os.listdir(first_action_path)
                    if os.path.isdir(os.path.join(first_action_path, seq))])

# Detect sequence length from first sequence
first_sequence_path = os.path.join(first_action_path, '0')
sequence_length = len([frame for frame in os.listdir(first_sequence_path)
                       if frame.endswith('.npy')])

print(f"✅ Number of sequences per action: {no_sequences}")
print(f"✅ Frames per sequence: {sequence_length}")

# Create label map
label_map = {label: num for num, label in enumerate(actions)}
print(f"\n📋 Label mapping: {label_map}")

# Load data
sequences, labels = [], []
print("\n📂 Loading data...")

for action in actions:
    action_sequences = 0
    for sequence in range(no_sequences):
        window = []
        for frame_num in range(sequence_length):
            try:
                res = np.load(os.path.join(DATA_PATH, action, str(sequence), f"{frame_num}.npy"))
                window.append(res)
            except Exception as e:
                print(f"⚠️  Warning: Could not load {action}/{sequence}/{frame_num}.npy")
                continue

        if len(window) == sequence_length:
            sequences.append(window)
            labels.append(label_map[action])
            action_sequences += 1
    print(f"   {action}: {action_sequences} sequences loaded")

X = np.array(sequences)
y = to_categorical(labels).astype(int)

print(f"\n📊 Data shape: {X.shape}")
print(f"📊 Labels shape: {y.shape}")
print(f"📊 Keypoints per frame: {X.shape[2]}")

# Check data balance
print("\n" + "=" * 60)
print("DATA BALANCE CHECK")
print("=" * 60)
for action in actions:
    count = np.sum(labels == label_map[action])
    percentage = (count / len(labels)) * 100
    print(f"{action:15s}: {count:3d} sequences ({percentage:.1f}%)")

# Split data with stratification for balanced splits
test_size = 0.2 if len(sequences) < 200 else 0.15
x_train, x_test, y_train, y_test = train_test_split(
    X, y,
    test_size=test_size,
    random_state=42,
    stratify=labels  # Ensures balanced train/test split
)

print(f"\n✂️  Training samples: {len(x_train)}")
print(f"✂️  Testing samples: {len(x_test)}")

# Calculate samples per action in training
samples_per_action = len(x_train) / len(actions)
print(f"✂️  Training samples per action: ~{samples_per_action:.0f}")

# Warning for small datasets
if samples_per_action < 40:
    print("\n" + "=" * 60)
    print("⚠️  WARNING: SMALL DATASET - HIGH RISK OF OVERFITTING!")
    print("=" * 60)
    print(f"   Current: ~{samples_per_action:.0f} training samples per action")
    print(f"   Recommended: At least 40-50 training samples per action")
    print(f"   Total needed: {len(actions) * 50}+ sequences")
    print("\n   To improve accuracy:")
    print("   1. Run ImprovedCollectData.py")
    print("   2. Collect 50-100 sequences per word WITH VARIATION")
    print("   3. Use different positions, speeds, angles")
    print("   4. Re-train the model")
    print("=" * 60 + "\n")

# Setup callbacks
log_dir = os.path.join('Logs')
tb_callback = TensorBoard(log_dir=log_dir)

# CRITICAL: Aggressive early stopping for small datasets
early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=30,  # Stop if no improvement for 30 epochs (reduced from 200!)
    restore_best_weights=True,
    verbose=1,
    min_delta=0.001  # Minimum change to qualify as improvement
)

# Learning rate reduction when plateau
reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,  # Reduce LR by 50%
    patience=15,  # After 15 epochs of no improvement
    min_lr=0.00001,
    verbose=1
)

callbacks = [tb_callback, early_stopping, reduce_lr]

# Build LSTM model with DROPOUT and regularization
print("\n" + "=" * 60)
print("BUILDING MODEL WITH ANTI-OVERFITTING MEASURES")
print("=" * 60)

model = Sequential([
    # First LSTM layer with dropout
    LSTM(64, return_sequences=True, activation='relu',
         input_shape=(sequence_length, X.shape[2]),
         kernel_regularizer=l2(0.01)),  # L2 regularization
    Dropout(0.3),  # Drop 30% of connections

    # Second LSTM layer with dropout
    LSTM(64, return_sequences=True, activation='relu',
         kernel_regularizer=l2(0.01)),
    Dropout(0.3),

    # Third LSTM layer
    LSTM(32, return_sequences=False, activation='relu',
         kernel_regularizer=l2(0.01)),
    Dropout(0.4),  # Higher dropout before dense layers

    # Dense layers with dropout
    Dense(64, activation='relu', kernel_regularizer=l2(0.01)),
    Dropout(0.4),

    Dense(32, activation='relu', kernel_regularizer=l2(0.01)),
    Dropout(0.3),

    # Output layer
    Dense(len(actions), activation='softmax')
])

# Compile with lower learning rate for stability
optimizer = Adam(learning_rate=0.0005)  # Lower than default 0.001
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['categorical_accuracy'])

print("\n📋 Model Architecture:")
model.summary()

print("\n🛡️  Anti-Overfitting Measures Applied:")
print("   ✅ Dropout layers (30-40%) after each LSTM/Dense")
print("   ✅ L2 regularization (0.01) on all layers")
print("   ✅ Early stopping (patience=30)")
print("   ✅ Learning rate reduction on plateau")
print("   ✅ Lower initial learning rate (0.0005)")
print("   ✅ Stratified train/test split")

# Train model
print("\n" + "=" * 60)
print("STARTING TRAINING")
print("=" * 60)
print(f"📊 Monitor training: tensorboard --logdir={log_dir}\n")

# Reasonable epochs based on dataset size
if samples_per_action < 30:
    epochs = 200
    print("⚠️  Very small dataset: Training for max 200 epochs")
elif samples_per_action < 50:
    epochs = 300
    print("⚠️  Small dataset: Training for max 300 epochs")
else:
    epochs = 500
    print("✅ Good dataset size: Training for max 500 epochs")

print(f"🛑 Early stopping will stop training if no improvement for 30 epochs\n")

history = model.fit(
    x_train, y_train,
    epochs=epochs,
    batch_size=16,  # Smaller batch size for small datasets
    callbacks=callbacks,
    validation_data=(x_test, y_test),
    verbose=1
)

actual_epochs = len(history.history['loss'])
print(f"\n✅ Training completed after {actual_epochs} epochs")

# Save model
model.save('actions_holistic.keras')
print(f"✅ Model saved as 'actions_holistic.keras'")

# Save actions list
np.save('actions_holistic_actions.npy', actions)
print(f"✅ Actions saved as 'actions_holistic_actions.npy'")

# Evaluate model
print("\n" + "=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

train_loss, train_accuracy = model.evaluate(x_train, y_train, verbose=0)
test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)

print(f"📊 Training Accuracy: {train_accuracy:.2%}")
print(f"📊 Testing Accuracy:  {test_accuracy:.2%}")
print(f"📊 Training Loss: {train_loss:.4f}")
print(f"📊 Testing Loss:  {test_loss:.4f}")

# Check for overfitting
accuracy_gap = train_accuracy - test_accuracy
print(f"\n📈 Accuracy Gap: {accuracy_gap:.2%}")

if accuracy_gap > 0.15:
    print("❌ WARNING: Significant overfitting detected!")
    print("   Training accuracy is much higher than test accuracy.")
    print("   Solutions:")
    print("   1. Collect more diverse training data")
    print("   2. Use ImprovedCollectData.py for better variation")
    print("   3. The model memorized training patterns")
elif accuracy_gap > 0.05:
    print("⚠️  Mild overfitting detected")
    print("   Consider collecting more varied data")
else:
    print("✅ No significant overfitting - model generalizes well!")

# Final recommendations
print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
if test_accuracy < 0.7:
    print("❌ Low accuracy detected. Recommendations:")
    print("   1. Collect MORE data (50-100 sequences per word)")
    print("   2. Use ImprovedCollectData.py for better variation")
    print("   3. Ensure good lighting and clear hand visibility")
    print("   4. Make distinct, consistent signs for each word")
elif test_accuracy < 0.85:
    print("⚠️  Moderate accuracy. Could be improved:")
    print("   1. Collect 20-30 more varied sequences per word")
    print("   2. Focus on making signs more distinct")
else:
    print("✅ Good accuracy! You can:")
    print("   1. Test with Run.py")
    print("   2. Run ModelDiagnostic.py to analyze performance")

print("\n   To test: python Run.py")
print("   To diagnose: python ModelDiagnostic.py")
print("=" * 60)