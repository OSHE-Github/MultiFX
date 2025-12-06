/*******************************************************************************

 name:             TremoloPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          https://oshe.io
 description:      TEMPLATE audio plugin.
 lastUpdated:	     Jan __ 2025 by ____

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        linux makefile

 type:             AudioProcessor
 mainClass:        TremoloProcessor

*******************************************************************************/

#pragma once


//==============================================================================
class TremoloProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    TremoloProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                           .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (rate = new juce::AudioParameterFloat ({"rate", 1}, "Rate", 0.0f, 20.0f, 10.0f)); // rate is in Hz
        addParameter (depth = new juce::AudioParameterFloat ({"depth", 1}, "Depth", 0.0f, 1.0f, 0.5f));
        addParameter (gain = new juce::AudioParameterFloat ({"gain", 1}, "Gain", 0.0f, 2.0f, 1.0f));
    }

    //==============================================================================
    void prepareToPlay (double, int) override
    {  
        position1 = 0; // Initial value for position within LFO signal for channel 1
        position2 = 0; // Initial value for position within LFO signal for channel 2
    }
    
    void releaseResources() override {}

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {  
        rateFloat = rate->get();
        depthFloat = depth->get();
        gainFloat = gain->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        w = 6.28318530718 * rateFloat;
    
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);
            
            if (channel == 0)
            {
                LFO = sin(position1 * w);
                
                for (int i = 0; i < buffer.getNumSamples(); ++i)
                {    
                    channelData[i] = channelData[i] * (depthFloat * LFO + (1.0f - depthFloat)) * gainFloat; // Tremolo and gain effects
                
                    position1 += (1 / sampleRate); // Increment position for channel 1 by sampling interval
                    if (position1 >= (1 / rateFloat)) // Check if position for channel 1 is beyond one LFO period
                    {
                        position1 = 0; // Resets position for channel 1 after one period
                    }
                }
            }
            else // Handles the second channel for stereo input but doesn't run for mono input
            {
                LFO = sin(position2 * w);
                
                for (int i = 0; i < buffer.getNumSamples(); ++i)
                {    
                    channelData[i] = channelData[i] * (depthFloat * LFO + (1.0f - depthFloat)) * gainFloat; // Tremolo and gain effects
                
                    position2 += (1 / sampleRate); // Increment position for channel 2 by sampling interval
                    if (position2 >= (1 / rateFloat)) // Check if position for channel 2 is beyond one LFO period
                    {
                        position2 = 0; // Resets position for channel 2 after one period
                    }
                }
            }   
        }
    }

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override          { return new juce::GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                        { return true;   }

    //==============================================================================
    const juce::String getName() const override                  { return "Tremolo Plugin"; }
    bool acceptsMidi() const override                      { return false; }
    bool producesMidi() const override                     { return false; }
    double getTailLengthSeconds() const override           { return 0; }

    //==============================================================================
    int getNumPrograms() override                          { return 1; }
    int getCurrentProgram() override                       { return 0; }
    void setCurrentProgram (int) override                  {}
    const juce::String getProgramName (int) override             { return "None"; }
    void changeProgramName (int, const juce::String&) override   {}

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override
    {
        juce::MemoryOutputStream (destData, true).writeFloat (*rate);
        juce::MemoryOutputStream (destData, true).writeFloat (*depth);
        juce::MemoryOutputStream (destData, true).writeFloat (*gain);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        rate->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        depth->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
    }

    //==============================================================================
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override
    {
        const auto& mainInLayout  = layouts.getChannelSet (true,  0);
        const auto& mainOutLayout = layouts.getChannelSet (false, 0);

        return (mainInLayout == mainOutLayout && (! mainInLayout.isDisabled()));
    }

private:
    //==============================================================================
    juce::AudioParameterFloat* rate;
    juce::AudioParameterFloat* depth;
    juce::AudioParameterFloat* gain;
    
    float rateFloat;
    float depthFloat;
    float gainFloat;
    
    double sampleRate;
    int totalNumInputChannels;
    float position1; // Current position within LFO signal for channel 1
    float position2; // Current position within LFO signal for channel 2
    float w; // w is in radians per second
    float LFO; // Low-frequency oscillator

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TremoloProcessor)
};
