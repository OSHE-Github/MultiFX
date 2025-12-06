/*
  ==============================================================================

    This file was auto-generated and contains the startup code for a PIP.

  ==============================================================================
*/

// This plugin was made by modifying the GainPluginDemo from File>Open Example>Plugins>GainPluginDemo
// https://github.com/juce-framework/JUCE/blob/master/examples/Plugins/GainPluginDemo.h

#include <JuceHeader.h>
#include "TremoloPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new TremoloProcessor();
}
