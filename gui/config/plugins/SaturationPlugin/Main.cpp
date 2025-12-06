#include <JuceHeader.h>
#include <math.h>
#include "SaturationPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SaturationProcessor();
}
