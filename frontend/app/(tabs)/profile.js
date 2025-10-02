import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { TextInput, Button, Text, Chip } from 'react-native-paper';
import { updateUserProfile } from '../../services/api';

export default function ProfileScreen() {
    const [householdSize, setHouseholdSize] = useState('2');
    const [diets, setDiets] = useState({ 'Vegan': false, 'Vegetarian': false, 'Gluten-Free': false });
    const [goals, setGoals] = useState({ 'Low-Carb': false, 'High-Protein': false, 'Low-Fat': false });
    const userId = 1; // Hardcoded user ID

    const handleDietToggle = (diet) => {
        setDiets(prev => ({ ...prev, [diet]: !prev[diet] }));
    };

    const handleGoalToggle = (goal) => {
        setGoals(prev => ({ ...prev, [goal]: !prev[goal] }));
    };

    const handleSave = async () => {
        const profileData = {
            household_size: parseInt(householdSize) || 2,
            dietary_restrictions: Object.keys(diets).filter(k => diets[k]),
            health_goals: Object.keys(goals).filter(k => goals[k]),
        };
        try {
            await updateUserProfile(userId, profileData);
            alert('Profile saved successfully!');
        } catch (error) {
            console.error('Failed to save profile:', error);
            alert('Failed to save profile.');
        }
    };

    return (
        <ScrollView style={styles.container}>
            <TextInput
                label="Household Size"
                value={householdSize}
                onChangeText={setHouseholdSize}
                keyboardType="numeric"
                style={styles.input}
            />
            <Text style={styles.label}>Dietary Restrictions</Text>
            <View style={styles.chipContainer}>
                {Object.keys(diets).map(diet => (
                    <Chip key={diet} selected={diets[diet]} onPress={() => handleDietToggle(diet)} style={styles.chip}>
                        {diet}
                    </Chip>
                ))}
            </View>

            <Text style={styles.label}>Health Goals</Text>
            <View style={styles.chipContainer}>
                {Object.keys(goals).map(goal => (
                    <Chip key={goal} selected={goals[goal]} onPress={() => handleGoalToggle(goal)} style={styles.chip}>
                        {goal}
                    </Chip>
                ))}
            </View>

            <Button mode="contained" onPress={handleSave} style={styles.button}>
                Save Profile
            </Button>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, padding: 16, backgroundColor: '#fff' },
    input: { marginBottom: 16 },
    label: { fontSize: 16, fontWeight: 'bold', marginTop: 16, marginBottom: 8 },
    chipContainer: { flexDirection: 'row', flexWrap: 'wrap' },
    chip: { marginRight: 8, marginBottom: 8 },
    button: { marginTop: 24 },
});