/*******************************************************************************

 name:             FunDistortionPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          https://oshe.io
 description:      fun distortion audio plugin. these won't sound like typical/practical distortion effects
 lastUpdated:	   April 4 2025 by Anna Andres

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors, juce_dsp,
                   juce_audio_utils, juce_core, juce_data_structures,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        linux makefile

 type:             AudioProcessor
 mainClass:        FunDistortionProcessor

*******************************************************************************/

#pragma once


//==============================================================================
class FunDistortionProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    // Constructor that lets you define input/output channels as well as parameters and their bounds
    FunDistortionProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                           .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 3.0f, 1.0f));
        addParameter (mode = new juce::AudioParameterInt({ "mode", 1 }, "Mode", 0, 4, 0));
        addParameter (lowthres = new juce::AudioParameterFloat({ "lowthres", 1 }, "Lower Threshold (Mode 1)", 0.5f, 9.0f, 0.5f));
        addParameter (highthres = new juce::AudioParameterFloat({ "highthres", 1 }, "(Higher) Threshold (Mode 1 & 4)", 0.5f, 9.0f, 0.5f));
        addParameter (nBits = new juce::AudioParameterFloat({ "nBits", 1 }, "Number of Bits (Mode 2)", 1.0f, 128.0f, 4.0f));
        addParameter (percentDrop = new juce::AudioParameterFloat({ "percentDrop", 1 }, "Sample Drop Percent (Mode 3)", 0.0f, 10.0f, 0.5f));
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
        
        //int modeValue = juce::roundToInt(mode->get());
        int modeValue = mode->get();
        
        // this seems counter-intuitive but the higher the parameter value, the closer the second calculations will be to 0
        auto hthres = lowthres->get();
        auto lthres = highthres->get();
        float lowThreshold = 0.05f / lthres;
        float highThreshold = 0.05f / hthres;
        
        // wavefold threshold will just use the upper threshold parameter instead of having its own (due to having a max of six params)
        float wavefoldThreshold = 0.05f / hthres;
        
        auto nbits = nBits->get(); // can be int or float for plugins
        auto ampValues = pow(2, nbits-1);
        
        auto pDrop = percentDrop->get();
        
        
        switch(modeValue) {
            case 1: // pause distortion - self made
                for (int channel = 0; channel < buffer.getNumChannels(); ++channel) {
                    auto* channelData = buffer.getWritePointer(channel);
                    for (int sample = 0; sample < buffer.getNumSamples(); ++sample) {
                        float processedSample = channelData[sample] * gainValue; // applying gain
                        if(processedSample <= (-1 * highThreshold)) {
                            processedSample = processedSample + (highThreshold - lowThreshold);
                        }
                        else if((-1 * highThreshold) < processedSample <= (-1 * lowThreshold)) {
                            processedSample = (-1 * lowThreshold);
                        }
                        else if(lowThreshold < processedSample <= highThreshold) {
                            processedSample = lowThreshold;
                        }
                        else if(processedSample > highThreshold) {
                            processedSample = processedSample - (highThreshold - lowThreshold);
                        }
                        channelData[sample] = processedSample;
                    }
                }
                break;
            case 2: // bit crushing
                for (int channel = 0; channel < buffer.getNumChannels(); ++channel) {
                    auto* channelData = buffer.getWritePointer(channel);
                    for (int sample = 0; sample < buffer.getNumSamples(); ++sample) {
                        float processedSample = ceil(ampValues*channelData[sample])*(1/ampValues); // apply bit crushing
                        channelData[sample] = gainValue*(processedSample);
                    }
                }
                break;
            case 3: // sample dropout
                for (int channel = 0; channel < buffer.getNumChannels(); ++channel) {
                    auto* channelData = buffer.getWritePointer(channel);
                    for (int sample = 0; sample < buffer.getNumSamples(); ++sample) {
                        int randomNum = fmod(rand(),100);
                        if(randomNum < pDrop) {
                            channelData[sample] = 0;
                            continue;
                        }
                        channelData[sample] = channelData[sample] * gainValue;
                    }
                }
                break;
            case 4: // wave folding
                for (int channel = 0; channel < buffer.getNumChannels(); ++channel) {
                    auto* channelData = buffer.getWritePointer(channel);
                    for (int sample = 0; sample < buffer.getNumSamples(); ++sample) {
                        float processedSample = channelData[sample] * gainValue; // applying gain
                        float dif = 0;
                        if(processedSample > wavefoldThreshold) {
                            dif = processedSample - wavefoldThreshold;
                            channelData[sample] = wavefoldThreshold - dif;
                        }
                        else if(processedSample < (-1 * wavefoldThreshold)) {
                            dif = wavefoldThreshold - processedSample;
                            channelData[sample] = wavefoldThreshold + dif;
                        }
                        else {
                            channelData[sample] = processedSample;
                        }
                    }
                }
                break;
            default: 
                // do nothing
                break;
        }
    }

    //==============================================================================
    // DO NOT CHANGE ANY OF THESE
    // This creates the GUI editor for the plugin
    juce::AudioProcessorEditor* createEditor() override          { return new juce::GenericAudioProcessorEditor (*this); }
    // We have a GUI editor for the plugin so we return true
    bool hasEditor() const override                        { return true;   }

    //==============================================================================
    const juce::String getName() const override                  { return "Fun Distortion PlugIn"; }
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
        juce::MemoryOutputStream (destData, true).writeInt (*mode);
        juce::MemoryOutputStream (destData, true).writeFloat (*lowthres);
        juce::MemoryOutputStream (destData, true).writeFloat (*highthres);
        juce::MemoryOutputStream (destData, true).writeFloat (*nBits);
        juce::MemoryOutputStream (destData, true).writeFloat (*percentDrop);
    }

    // This function recalls the state of the parameters from the last session ran and restores it into the parameter
    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        mode->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
        lowthres->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        highthres->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        nBits->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        percentDrop->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
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
    juce::AudioParameterInt* mode;
    juce::AudioParameterFloat* lowthres;
    juce::AudioParameterFloat* highthres;
    juce::AudioParameterFloat* nBits;
    juce::AudioParameterFloat* percentDrop;

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FunDistortionProcessor)
};

