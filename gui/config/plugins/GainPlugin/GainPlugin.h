/*******************************************************************************

 name:             GainPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          https://oshe.io
 description:      gain audio plugin.
 lastUpdated:	   April 1 2025 by Anna Andres

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors, juce_dsp,
                   juce_audio_utils, juce_core, juce_data_structures,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        linux makefile

 type:             AudioProcessor
 mainClass:        GainProcessor

*******************************************************************************/

#pragma once


//==============================================================================
class GainProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    // Constructor that lets you define input/output channels as well as parameters and their bounds
    GainProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                           .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 3.0f, 0.5f));
    }

    //==============================================================================
    // This function is used before audio processing. It lets you initialize variables and set up any other resources prior to running the plugin
    void prepareToPlay (double, int) override {}
    // This function is usually called after the plugin stops taking in audio. It can deallocate any memory used and clean out buffers
    void releaseResources() override {}

    // This is where all the audio processing happens. One buffer of audio input is handled at a time.
    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        
        auto gainValue = gain->get();
        
        for (int channel = 0; channel < buffer.getNumChannels(); ++channel) 
        {
            auto* channelData = buffer.getWritePointer(channel);
            for (int sample = 0; sample < buffer.getNumSamples(); ++sample) 
            {
                channelData[sample] = channelData[sample] * gainValue; // apply gain
            }
        }
    }

    //==============================================================================
    // DO NOT CHANGE ANY OF THESE
    // This creates the GUI editor for the plugin
    juce::AudioProcessorEditor* createEditor() override          { return new juce::GenericAudioProcessorEditor (*this); }
    // We have a GUI editor for the plugin so we return true
    bool hasEditor() const override                        { return true;   }

    //==============================================================================
    const juce::String getName() const override                  { return "Gain PlugIn"; }
    // This function returns a boolean for whether or not the plugin accepts Midi input. We don't. so this will be false
    bool acceptsMidi() const override                      { return false; }
    // This function returns a boolean for whether or not the plugin has Midi output. We don't. so this will be false
    bool producesMidi() const override                     { return false; }
    // This specifies how much longer there is output when the input stops. This would be helpful for reverb/delay but not so much for distortion/gain
    // A 0 tail length means that the output stops as soon as the input stops
    double getTailLengthSeconds() const override           { return 0; } //TODO: Change tail length if desired

    //==============================================================================
    // DO NOT CHANGE ANY OF THESE
    // This returns the number of presets/configurations for the plugin. We only have a default configuration so we return 1
    int getNumPrograms() override                          { return 1; }
    // This returns the index of the currently selected program. This will always be 0 for this plugin
    int getCurrentProgram() override                       { return 0; }
    // This allows the user to switch to a different program if you have multiple
    void setCurrentProgram (int) override                  {}
    // This gives you the name of the program for a given index
    const juce::String getProgramName (int) override             { return "None"; }
    // This allows you to change the name of a program at the given index
    void changeProgramName (int, const juce::String&) override   {}

    //==============================================================================
    // This function saves the current state of each parameter to memory so that we can load the state of each parameter 
    // in the next session of running the pedal
    void getStateInformation (juce::MemoryBlock& destData) override
    {
	    juce::MemoryOutputStream (destData, true).writeFloat (*gain);
    }

    // This function recalls the state of the parameters from the last session ran and restores it into the parameter
    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
    }

    //==============================================================================
    // This function checks to see if the requested input/output configuration is compatible with the coded plugin
    // DO NOT CHANGE THIS FUNCTION
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override
    {
        const auto& mainInLayout  = layouts.getChannelSet (true,  0);
        const auto& mainOutLayout = layouts.getChannelSet (false, 0);

        return (mainInLayout == mainOutLayout && (! mainInLayout.isDisabled()));
    }

private:
    //==============================================================================
    juce::AudioParameterFloat* gain;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (GainProcessor)
};

