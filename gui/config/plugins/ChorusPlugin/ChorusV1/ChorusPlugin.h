/*
  ==============================================================================

   This file is part of the JUCE framework examples.
   Copyright (c) Raw Material Software Limited

   The code included in this file is provided under the terms of the ISC license
   http://www.isc.org/downloads/software-support-policy/isc-license. Permission
   to use, copy, modify, and/or distribute this software for any purpose with or
   without fee is hereby granted provided that the above copyright notice and
   this permission notice appear in all copies.

   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
   REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
   AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
   INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
   LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
   OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
   PERFORMANCE OF THIS SOFTWARE.

  ==============================================================================
*/

/*******************************************************************************
 The block below describes the properties of this PIP. A PIP is a short snippet
 of code that can be read by the Projucer and used to generate a JUCE project.

 BEGIN_JUCE_PIP_METADATA

 name:             ChorusPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          oshe.io
 description:      Chorus audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporter:         Linux Makefile

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        ChorusProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class ChorusProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    ChorusProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 1.0f, 0.5f));
        addParameter (rate = new juce::AudioParameterFloat ({"rate", 1}, "Rate", 0.0f, 10.0f, 5.0f)); // rate is in Hz
        addParameter (depth = new juce::AudioParameterFloat ({"depth", 1}, "Depth", 0.0f, 1.0f, 0.5f));
        addParameter (delay = new juce::AudioParameterFloat ({ "delay", 1 }, "Delay", 0.01f, 0.1f, 0.03f)); // delay is in seconds
        addParameter (feedback = new juce::AudioParameterFloat ({ "feedback", 1 }, "Feedback", 0.0f, 1.0f, 0.2f));
        addParameter (mix = new juce::AudioParameterFloat ({ "mix", 1 }, "Mix", 0.0f, 1.0f, 0.5f));
    }

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override
    {  
        // Sets specs for a JUCE DSP processor
        juce::dsp::ProcessSpec spec;
        spec.maximumBlockSize = samplesPerBlock;
        spec.sampleRate = sampleRate;
        spec.numChannels = getTotalNumOutputChannels();
        
        
        // Delay Lines
        
        // Initializes both delay lines
        chnl1delay.prepare (spec);
        chnl2delay.prepare (spec);
        
        // Since the delay parameter is limited to a maximum of 0.1s, and based on delayInSamples
        // which can double the value of the delay parameter based on the LFO, the maximum possible number of samples is sampleRate in samples/s * 0.2s
        chnl1delay.setMaximumDelayInSamples (sampleRate * 0.2f);
        chnl2delay.setMaximumDelayInSamples (sampleRate * 0.2f);
        
        // Converts delay in seconds to delay in samples and updates delay of both delay lines
        delayFloat = delay->get();
        chnl1delay.setDelay (delayFloat * sampleRate);
        chnl2delay.setDelay (delayFloat * sampleRate);
        
        
        // LFOs
        
        // Initializes both LFOs
        chnl1LFO.prepare (spec);
        chnl2LFO.prepare (spec);
        
        // Updates rate of both LFOs
        rateFloat = rate->get();
        chnl1LFO.setFrequency (rateFloat);
        chnl2LFO.setFrequency (rateFloat);
    }
    
    void releaseResources() override {}

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        gainFloat = gain->get();
        rateFloat = rate->get();
        depthFloat = depth->get();
        delayFloat = delay->get();
        feedbackFloat = feedback->get();
        mixFloat = mix->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        chnl1delay.setDelay (delayFloat * sampleRate);
        chnl2delay.setDelay (delayFloat * sampleRate);
        
        chnl1LFO.setFrequency (rateFloat);
        chnl2LFO.setFrequency (rateFloat);
        
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);
            
            if (channel == 0)
            {
                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                {
                    lfoValue = chnl1LFO.processSample(0.0f);
                    delayInSamples = (lfoValue * delayFloat + delayFloat) * sampleRate;
                    
                    drySample = channelData[sample];
                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                    wetSample = (wetSample * ((depthFloat/5.0f) * (0.5f * abs(lfoValue) + 0.5f) + (1.0f - (depthFloat/5.0f)))); // Amplitude Modulation
                    chnl1delay.pushSample(channel, channelData[sample]);//chnl1delay.pushSample(channel, drySample + wetSample * feedbackFloat); // Feedback
                    
                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay
                    channelData[sample] *= gainFloat; // Gain
                }
            }
            else // Handles the second channel for stereo input but doesn't run for mono input
            {
                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                {
                    lfoValue = chnl2LFO.processSample(0.0f);
                    delayInSamples = (lfoValue * delayFloat + delayFloat) * sampleRate;
                    
                    drySample = channelData[sample];
                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                    wetSample = (wetSample * ((depthFloat/5.0f) * (0.5f * abs(lfoValue) + 0.5f) + (1.0f - (depthFloat/5.0f))));
                    chnl2delay.pushSample(channel, channelData[sample]);//chnl2delay.pushSample(channel, drySample + wetSample * feedbackFloat);
                    
                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                    channelData[sample] *= gainFloat;
                }
            }  
        }
    }

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override         { return new juce::GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                             { return true;   }

    //==============================================================================
    const juce::String getName() const override                 { return "Chorus PlugIn"; }
    bool acceptsMidi() const override                           { return false; }
    bool producesMidi() const override                          { return false; }
    double getTailLengthSeconds() const override                { return 0; }

    //==============================================================================
    int getNumPrograms() override                               { return 1; }
    int getCurrentProgram() override                            { return 0; }
    void setCurrentProgram (int) override                       {}
    const juce::String getProgramName (int) override            { return "None"; }
    void changeProgramName (int, const juce::String&) override  {}

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override
    {
        juce::MemoryOutputStream (destData, true).writeFloat (*gain);
        juce::MemoryOutputStream (destData, true).writeFloat (*rate);
        juce::MemoryOutputStream (destData, true).writeFloat (*depth);
        juce::MemoryOutputStream (destData, true).writeFloat (*delay);
        juce::MemoryOutputStream (destData, true).writeFloat (*feedback);
        juce::MemoryOutputStream (destData, true).writeFloat (*mix);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        rate->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        depth->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        delay->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        feedback->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        mix->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
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
    juce::AudioParameterFloat* gain;
    juce::AudioParameterFloat* rate;
    juce::AudioParameterFloat* depth;
    juce::AudioParameterFloat* delay;
    juce::AudioParameterFloat* feedback;
    juce::AudioParameterFloat* mix;
    
    float gainFloat;
    float rateFloat;
    float depthFloat;
    float delayFloat;
    float feedbackFloat;
    float mixFloat;
    
    float lfoValue;
    float drySample;
    float wetSample;
    double sampleRate;
    int totalNumInputChannels;
    int delayInSamples;
    
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> chnl1delay;
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> chnl2delay;
    
    // The last argument for the following lines is the number of points in the lookup table
    juce::dsp::Oscillator<float> chnl1LFO { [](float x) { return std::sin (x); }, 200 };
    juce::dsp::Oscillator<float> chnl2LFO { [](float x) { return std::sin (x); }, 200 };
    
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (ChorusProcessor)
};
